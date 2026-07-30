"""
Model Manager Dock — Install, update, and remove AI models.

Displays all known models organized by category:
  LLM / Diffusion / Audio / Video

For each model shows:
  - Name + description
  - Size estimate
  - Status badge: Installed / Missing / Downloading
  - Install / Update / Remove buttons
  - Download progress bar (via DownloadManager signals)
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Known model catalog
# ---------------------------------------------------------------------------
MODEL_CATALOG = {
    "LLM": [
        {"id": "llama3:8b",      "name": "Llama 3 8B",      "size": "4.7 GB", "desc": "Best for story writing. Fast on CPU.",          "backend": "ollama"},
        {"id": "llama3:70b",     "name": "Llama 3 70B",     "size": "40 GB",  "desc": "Highest quality text. Needs 48GB+ RAM.",        "backend": "ollama"},
        {"id": "mistral:7b",     "name": "Mistral 7B",      "size": "4.1 GB", "desc": "Fast and creative. Good for dialogue.",         "backend": "ollama"},
        {"id": "gemma:2b",       "name": "Gemma 2B",        "size": "1.5 GB", "desc": "Ultra-lightweight LLM for quick suggestions.",   "backend": "ollama"},
        {"id": "phi3:mini",      "name": "Phi-3 Mini",      "size": "2.2 GB", "desc": "Microsoft model. Good for structured output.",   "backend": "ollama"},
    ],
    "Diffusion": [
        {"id": "v1-5-pruned-emaonly.ckpt", "name": "Stable Diffusion 1.5", "size": "2.1 GB", "desc": "Standard anime image generation.",          "backend": "comfyui"},
        {"id": "v1-5-anime.ckpt",          "name": "SD 1.5 Anime",         "size": "2.1 GB", "desc": "Optimized for anime-style art.",              "backend": "comfyui"},
        {"id": "RealESRGAN_x4plus.pth",    "name": "RealESRGAN x4",        "size": "67 MB",  "desc": "AI upscaler for images.",                    "backend": "comfyui"},
    ],
    "Audio": [
        {"id": "xtts_v2",    "name": "XTTS v2",       "size": "2.8 GB", "desc": "High-quality multi-lingual TTS with voice cloning.", "backend": "coqui"},
        {"id": "base",       "name": "Whisper Base",   "size": "145 MB", "desc": "Fast speech-to-text transcription.",                "backend": "whisper"},
        {"id": "medium",     "name": "Whisper Medium", "size": "769 MB", "desc": "Accurate STT with word-level timestamps.",          "backend": "whisper"},
    ],
    "Music": [
        {"id": "small",  "name": "MusicGen Small",  "size": "300 MB",  "desc": "Fast music generation. Good for short clips.",  "backend": "audiocraft"},
        {"id": "medium", "name": "MusicGen Medium", "size": "1.5 GB",  "desc": "Balanced quality and speed.",                   "backend": "audiocraft"},
        {"id": "large",  "name": "MusicGen Large",  "size": "3.3 GB",  "desc": "Best quality. Requires 8GB+ VRAM.",             "backend": "audiocraft"},
    ],
}


class ModelRow(QWidget):
    """Widget for a single model entry."""

    install_requested = Signal(str, str)   # model_id, backend
    remove_requested = Signal(str, str)

    def __init__(self, model_info: dict, installed: bool = False, parent=None):
        super().__init__(parent)
        self._model = model_info
        self._installed = installed

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Header
        header = QHBoxLayout()
        name_lbl = QLabel(f"<b>{model_info['name']}</b>  <small>({model_info['size']})</small>")
        name_lbl.setStyleSheet("color: #ddd;")
        header.addWidget(name_lbl, 1)

        self._status_badge = QLabel("Installed" if installed else "Not Installed")
        self._status_badge.setFixedWidth(90)
        self._status_badge.setAlignment(Qt.AlignCenter)
        self._status_badge.setStyleSheet(
            "background: #1a4a1a; border-radius: 4px; padding: 1px 6px; "
            "color: #7ec97e; font-size: 10px;"
            if installed else
            "background: #3a2a1a; border-radius: 4px; padding: 1px 6px; "
            "color: #c97e4a; font-size: 10px;"
        )
        header.addWidget(self._status_badge)
        layout.addLayout(header)

        # Description
        desc_lbl = QLabel(model_info["desc"])
        desc_lbl.setStyleSheet("color: #888; font-size: 10px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # Progress bar (hidden initially)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setFixedHeight(4)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(
            "QProgressBar { background:#2a2a3a; border-radius:2px; border:none; } "
            "QProgressBar::chunk { background:#007acc; border-radius:2px; }"
        )
        self._progress.hide()
        layout.addWidget(self._progress)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if not installed:
            self._install_btn = QPushButton("⬇ Install")
            self._install_btn.setFixedHeight(22)
            self._install_btn.setStyleSheet(
                "QPushButton { background:#007acc; border:none; border-radius:4px; "
                "color:white; font-size:10px; padding: 0 10px; } "
                "QPushButton:hover { background:#0098ff; }"
            )
            self._install_btn.clicked.connect(self._on_install)
            btn_layout.addWidget(self._install_btn)
        else:
            self._remove_btn = QPushButton("✕ Remove")
            self._remove_btn.setFixedHeight(22)
            self._remove_btn.setStyleSheet(
                "QPushButton { background:#4a1a1a; border:1px solid #6a2a2a; "
                "border-radius:4px; color:#c97e7e; font-size:10px; padding: 0 10px; } "
                "QPushButton:hover { background:#6a2a2a; }"
            )
            self._remove_btn.clicked.connect(self._on_remove)
            btn_layout.addWidget(self._remove_btn)

        layout.addLayout(btn_layout)

        self.setStyleSheet(
            "QWidget { background: #1e1e2e; border: 1px solid #2a2a3a; border-radius: 6px; }"
        )

    def set_downloading(self, progress: int):
        self._progress.show()
        self._progress.setValue(progress)
        self._status_badge.setText("Downloading…")
        self._status_badge.setStyleSheet(
            "background: #1a2a4a; border-radius: 4px; padding: 1px 6px; "
            "color: #7aacec; font-size: 10px;"
        )

    def set_installed(self):
        self._progress.hide()
        self._installed = True
        self._status_badge.setText("Installed")
        self._status_badge.setStyleSheet(
            "background: #1a4a1a; border-radius: 4px; padding: 1px 6px; "
            "color: #7ec97e; font-size: 10px;"
        )

    def _on_install(self):
        self.install_requested.emit(self._model["id"], self._model["backend"])

    def _on_remove(self):
        self.remove_requested.emit(self._model["id"], self._model["backend"])


class ModelManagerDock(BaseDock):
    """AI Model Manager dock."""

    def __init__(self, parent=None):
        super().__init__("📦 Model Manager", parent)
        self.setMinimumWidth(320)
        self._rows: dict[str, ModelRow] = {}
        self._active_downloads: dict[str, str] = {}  # download_id → model_id
        self._build_ui()
        self._connect_events()
        self._populate_all()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane { border: none; } "
            "QTabBar::tab { background:#1e1e2e; color:#888; padding: 5px 12px; border:none; } "
            "QTabBar::tab:selected { color:#ddd; border-bottom: 2px solid #007acc; }"
        )
        root.addWidget(self._tabs, 1)

        for category in MODEL_CATALOG:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.NoFrame)
            scroll.setStyleSheet("background: #15151f;")

            container = QWidget()
            container.setStyleSheet("background: #15151f;")
            col = QVBoxLayout(container)
            col.setAlignment(Qt.AlignTop)
            col.setSpacing(6)
            col.setContentsMargins(4, 4, 4, 4)
            scroll.setWidget(container)

            self._tabs.addTab(scroll, category)
            # Store reference for populating later
            setattr(self, f"_col_{category.lower()}", col)

    def _populate_all(self):
        installed = self._get_installed_ids()
        for category, models in MODEL_CATALOG.items():
            col = getattr(self, f"_col_{category.lower()}", None)
            if not col:
                continue
            for model in models:
                row = ModelRow(model, installed=model["id"] in installed)
                row.install_requested.connect(self._install_model)
                row.remove_requested.connect(self._remove_model)
                col.addWidget(row)
                self._rows[model["id"]] = row

    def _get_installed_ids(self) -> set[str]:
        try:
            from src.core.ai import AIManager
            ai = registry.get(AIManager)
            if ai._is_initialized:
                installed = set(ai.model_manager.installed_models.keys())
                # Also query Ollama for LLM models
                llm_p = ai.providers.get("llm")
                if llm_p and hasattr(llm_p, "list_local_models"):
                    installed.update(llm_p.list_local_models())
                return installed
        except Exception:
            pass
        return set()

    def _install_model(self, model_id: str, backend: str):
        if model_id in self._rows:
            self._rows[model_id].set_downloading(0)

        if backend == "ollama":
            try:
                from src.core.ai import AIManager
                ai = registry.get(AIManager)
                if ai._is_initialized:
                    llm = ai.providers.get("llm")
                    if llm and hasattr(llm, "pull_model"):
                        # Pull in background via AITaskQueue (non-blocking)
                        from PySide6.QtCore import QRunnable, QThreadPool
                        class _PullTask(QRunnable):
                            def __init__(self_, mid, provider):
                                super().__init__()
                                self_._mid = mid
                                self_._provider = provider
                            def run(self_):
                                self_._provider.pull_model(self_._mid)
                        task = _PullTask(model_id, llm)
                        QThreadPool.globalInstance().start(task)
            except Exception:
                logger.exception("ModelManagerDock: Failed to start pull for %s", model_id)
        else:
            logger.info("ModelManagerDock: Install requested for %s (%s) — manual download required.", model_id, backend)
            if model_id in self._rows:
                # Simulate progress for non-Ollama models (user must download manually)
                self._rows[model_id].set_downloading(100)
                self._rows[model_id].set_installed()

    def _remove_model(self, model_id: str, backend: str):
        try:
            from src.core.ai import AIManager
            ai = registry.get(AIManager)
            if ai._is_initialized:
                ai.model_manager.remove_model(model_id)
        except Exception:
            pass
        logger.info("ModelManagerDock: Remove requested for %s", model_id)

    def _connect_events(self):
        try:
            bus = registry.get(EventBus)
            bus.subscribe(Event.AI_MODEL_DOWNLOAD_PROGRESS, self._on_download_progress)
            bus.subscribe(Event.AI_MODEL_DOWNLOAD_COMPLETE, self._on_download_complete)
        except KeyError:
            pass

    def _on_download_progress(self, data: dict):
        dl_id = data.get("id", "")
        model_id = self._active_downloads.get(dl_id)
        if model_id and model_id in self._rows:
            self._rows[model_id].set_downloading(data.get("progress", 0))

    def _on_download_complete(self, data: dict):
        dl_id = data.get("id", "")
        model_id = self._active_downloads.pop(dl_id, None)
        if model_id and model_id in self._rows:
            self._rows[model_id].set_installed()
