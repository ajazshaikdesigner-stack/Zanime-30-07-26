"""
AI Job Manager Dock — full-featured replacement for the minimal AIConsoleDock.

Displays every active and recent AI job with:
  - Progress bar per job
  - ETA estimate
  - Type badge (text / image / audio / music)
  - Cancel / Pause / Resume controls
  - GPU % and VRAM bar (polled via psutil if available)
  - Persists completed jobs in session (last 50)
"""

import logging
import time
from collections import deque

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry

logger = logging.getLogger(__name__)

_PROVIDER_BADGE = {
    "llm":       ("💬 Text",  "#3a6a9a"),
    "diffusion": ("🎨 Image", "#7a4a9a"),
    "tts":       ("🎙 Voice", "#3a8a5a"),
    "stt":       ("👂 STT",   "#5a7a3a"),
    "music":     ("🎵 Music", "#8a6a2a"),
}


class JobRow(QWidget):
    """Widget representing a single AI job in the job list."""

    def __init__(self, task_id: str, provider: str, prompt_preview: str, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self._start_time = time.time()
        self._progress = 0
        self._done = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(3)

        # Header row: badge + label + eta
        header = QHBoxLayout()
        header.setSpacing(6)

        badge_text, badge_color = _PROVIDER_BADGE.get(provider, ("⚙ Task", "#555"))
        badge = QLabel(badge_text)
        badge.setStyleSheet(
            f"background: {badge_color}; border-radius: 4px; "
            "padding: 1px 6px; color: white; font-size: 10px;"
        )
        badge.setFixedWidth(72)
        header.addWidget(badge)

        preview = prompt_preview[:50] + ("…" if len(prompt_preview) > 50 else "")
        self._name_lbl = QLabel(preview)
        self._name_lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        header.addWidget(self._name_lbl, 1)

        self._eta_lbl = QLabel("Queued")
        self._eta_lbl.setStyleSheet("color: #888; font-size: 10px;")
        header.addWidget(self._eta_lbl)

        layout.addLayout(header)

        # Progress bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(6)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            "QProgressBar { background:#2a2a3a; border-radius:3px; border:none; } "
            "QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #007acc,stop:1 #00d4ff); border-radius:3px; }"
        )
        layout.addWidget(self._bar)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        ctrl.addStretch()

        for label, slot in [("⏸", self._pause), ("▶", self._resume), ("✕", self._cancel)]:
            btn = QPushButton(label)
            btn.setFixedSize(22, 18)
            btn.setStyleSheet(
                "QPushButton { background:#333; border:1px solid #555; border-radius:3px; "
                "color:#ccc; font-size:11px; } QPushButton:hover { background:#444; }"
            )
            btn.clicked.connect(slot)
            ctrl.addWidget(btn)

        layout.addLayout(ctrl)

        # Styling
        self.setStyleSheet(
            "QWidget { background:#1e1e2e; border:1px solid #2a2a3a; border-radius:6px; }"
        )
        self.setFixedHeight(90)

    def update_progress(self, progress: int, msg: str = ""):
        self._progress = progress
        self._bar.setValue(progress)
        elapsed = time.time() - self._start_time
        if progress > 5:
            eta_total = elapsed / (progress / 100.0)
            eta_remaining = max(0, eta_total - elapsed)
            self._eta_lbl.setText(f"ETA {eta_remaining:.0f}s")
        else:
            self._eta_lbl.setText("Running…")

    def mark_done(self, success: bool):
        self._done = True
        self._bar.setValue(100)
        elapsed = time.time() - self._start_time
        self._eta_lbl.setText(f"{'✓ Done' if success else '✗ Failed'} in {elapsed:.1f}s")
        self._bar.setStyleSheet(
            "QProgressBar { background:#2a2a3a; border-radius:3px; border:none; } "
            "QProgressBar::chunk { background:#2a8a2a; border-radius:3px; }"
            if success else
            "QProgressBar { background:#2a2a3a; border-radius:3px; border:none; } "
            "QProgressBar::chunk { background:#8a2a2a; border-radius:3px; }"
        )

    def _cancel(self):
        try:
            from src.core.ai import AIManager
            registry.get(AIManager).task_queue.cancel_job(self.task_id)
        except Exception:
            pass

    def _pause(self):
        try:
            from src.core.ai import AIManager
            registry.get(AIManager).task_queue.pause_job(self.task_id)
        except Exception:
            pass

    def _resume(self):
        try:
            from src.core.ai import AIManager
            registry.get(AIManager).task_queue.resume_job(self.task_id)
        except Exception:
            pass


class AIJobManagerDock(BaseDock):
    """Full-featured AI job manager with GPU/VRAM monitoring."""

    def __init__(self, parent=None):
        super().__init__("⚡ AI Jobs", parent)
        self.setMinimumWidth(280)

        self._rows: dict[str, JobRow] = {}
        self._completed: deque = deque(maxlen=50)
        self._task_meta: dict[str, dict] = {}  # task_id → {provider, prompt}

        self._build_ui()
        self._connect_events()

        # GPU/VRAM polling (every 3 seconds, if psutil available)
        self._gpu_timer = QTimer(self)
        self._gpu_timer.timeout.connect(self._update_system_stats)
        self._gpu_timer.start(3000)

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # System stats bar
        stats_layout = QHBoxLayout()
        self._cpu_lbl = QLabel("CPU: —")
        self._ram_lbl = QLabel("RAM: —")
        self._vram_lbl = QLabel("VRAM: —")
        for lbl in [self._cpu_lbl, self._ram_lbl, self._vram_lbl]:
            lbl.setStyleSheet("color: #888; font-size: 10px; padding: 2px;")
            stats_layout.addWidget(lbl)
        stats_layout.addStretch()

        self._clear_btn = QPushButton("Clear Done")
        self._clear_btn.setFixedHeight(20)
        self._clear_btn.setStyleSheet(
            "QPushButton { background:#333; border:1px solid #555; border-radius:3px; "
            "color:#aaa; font-size:10px; padding: 0 8px; } "
            "QPushButton:hover { background:#444; }"
        )
        self._clear_btn.clicked.connect(self._clear_completed)
        stats_layout.addWidget(self._clear_btn)
        root.addLayout(stats_layout)

        # Active job count label
        self._active_lbl = QLabel("No active jobs.")
        self._active_lbl.setStyleSheet("color: #666; font-size: 11px; padding: 2px 4px;")
        root.addWidget(self._active_lbl)

        # Scroll area for job rows
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet("background: #15151f;")

        self._jobs_container = QWidget()
        self._jobs_container.setStyleSheet("background: #15151f;")
        self._jobs_layout = QVBoxLayout(self._jobs_container)
        self._jobs_layout.setAlignment(Qt.AlignTop)
        self._jobs_layout.setSpacing(4)
        self._jobs_layout.setContentsMargins(2, 2, 2, 2)
        self._scroll.setWidget(self._jobs_container)
        root.addWidget(self._scroll, 1)

    def _connect_events(self):
        try:
            bus = registry.get(EventBus)
            bus.subscribe(Event.AI_TASK_STARTED, self._on_started)
            bus.subscribe(Event.AI_TASK_PROGRESS, self._on_progress)
            bus.subscribe(Event.AI_TASK_COMPLETED, self._on_completed)
            bus.subscribe(Event.AI_TASK_FAILED, self._on_failed)
        except KeyError:
            logger.debug("AIJobManagerDock: EventBus not available.")

    def _on_started(self, task_id: str):
        # Retrieve provider + prompt from the task queue if available
        provider = "llm"
        prompt = "AI task"
        try:
            from src.core.ai import AIManager
            ai = registry.get(AIManager)
            task = ai.task_queue.active_tasks.get(task_id)
            if task:
                provider = getattr(task, "_provider_type", provider)
                prompt = task.prompt
        except Exception:
            pass

        row = JobRow(task_id, provider, prompt)
        self._rows[task_id] = row
        self._jobs_layout.insertWidget(0, row)  # New jobs at top
        self._update_count()

    def _on_progress(self, data: dict):
        task_id = data.get("id", "")
        if task_id in self._rows:
            self._rows[task_id].update_progress(
                data.get("progress", 0), data.get("msg", "")
            )

    def _on_completed(self, data: dict):
        task_id = data.get("id", "")
        if task_id in self._rows:
            self._rows[task_id].mark_done(success=True)
            self._completed.append(task_id)
        self._update_count()

    def _on_failed(self, data: dict):
        task_id = data.get("id", "")
        if task_id in self._rows:
            self._rows[task_id].mark_done(success=False)
        self._update_count()

    def _clear_completed(self):
        for task_id in list(self._completed):
            if task_id in self._rows:
                row = self._rows.pop(task_id)
                self._jobs_layout.removeWidget(row)
                row.deleteLater()
        self._completed.clear()
        self._update_count()

    def _update_count(self):
        active = len(self._rows) - len(self._completed)
        if active > 0:
            self._active_lbl.setText(f"{active} active job{'s' if active != 1 else ''}…")
            self._active_lbl.setStyleSheet("color: #7ec97e; font-size: 11px; padding: 2px 4px;")
        else:
            self._active_lbl.setText("No active jobs.")
            self._active_lbl.setStyleSheet("color: #666; font-size: 11px; padding: 2px 4px;")

    def _update_system_stats(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            self._cpu_lbl.setText(f"CPU: {cpu:.0f}%")
            self._ram_lbl.setText(f"RAM: {ram.percent:.0f}%")

            # Try GPU VRAM (requires GPUtil or pynvml)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    g = gpus[0]
                    self._vram_lbl.setText(
                        f"VRAM: {g.memoryUsed:.0f}/{g.memoryTotal:.0f}MB"
                    )
            except ImportError:
                self._vram_lbl.setText("VRAM: N/A")
        except ImportError:
            self._cpu_lbl.setText("CPU: N/A")
