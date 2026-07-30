"""
AI Copilot Dock — Global context-aware AI assistant for ZANIME.

Features:
  - Chat-style conversation history with styled message bubbles
  - Context-awareness: reads active workspace + project name
  - One-click quick action buttons (Generate Story, Suggest Scene, etc.)
  - Conversation history persisted per-session
  - Subscribes to WORKSPACE_CHANGED to update context automatically
"""

import logging
import time

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry

logger = logging.getLogger(__name__)


class MessageBubble(QWidget):
    """A single chat message bubble — user or assistant."""

    USER_STYLE = """
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #007acc,stop:1 #0098ff);
        border-radius: 12px 12px 2px 12px;
        padding: 8px 12px;
        color: white;
    """
    ASSISTANT_STYLE = """
        background: #2a2a3a;
        border-radius: 12px 12px 12px 2px;
        padding: 8px 12px;
        color: #e0e0e0;
        border: 1px solid #3a3a4a;
    """
    SYSTEM_STYLE = """
        background: #1a2a1a;
        border-radius: 8px;
        padding: 6px 10px;
        color: #7ec97e;
        font-style: italic;
    """

    def __init__(self, text: str, role: str = "assistant", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        if role == "user":
            label.setStyleSheet(self.USER_STYLE)
            layout.addStretch()
            layout.addWidget(label)
        elif role == "system":
            label.setStyleSheet(self.SYSTEM_STYLE)
            layout.addWidget(label)
            layout.addStretch()
        else:
            label.setStyleSheet(self.ASSISTANT_STYLE)
            layout.addWidget(label)
            layout.addStretch()


class AICopilotDock(BaseDock):
    """
    Global AI Copilot dock that provides a chat interface powered by the
    OllamaProvider through ZanimeAIAPI.chat().
    """

    _response_ready = Signal(str)  # Emitted from background thread → main thread

    def __init__(self, parent=None):
        super().__init__("✦ AI Copilot", parent)
        self.setMinimumWidth(300)

        self._context = "No project loaded."
        self._active_workspace = "Home"
        self._pending_task_id: str | None = None
        self._conversation: list[dict] = []

        self._build_ui()
        self._connect_events()
        self._add_system_message(
            "ZANIME AI Copilot ready. Ask me anything about your project!"
        )

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root_layout = QVBoxLayout(self.container)
        root_layout.setContentsMargins(4, 4, 4, 4)
        root_layout.setSpacing(4)

        # Context label
        self._context_label = QLabel("Context: No project")
        self._context_label.setStyleSheet(
            "color: #888; font-size: 10px; padding: 2px 4px;"
        )
        root_layout.addWidget(self._context_label)

        # Chat scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet("background: #1a1a2e;")

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setAlignment(Qt.AlignTop)
        self._chat_layout.setSpacing(6)
        self._chat_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll.setWidget(self._chat_container)
        root_layout.addWidget(self._scroll, 1)

        # Thinking indicator
        self._thinking_bar = QProgressBar()
        self._thinking_bar.setRange(0, 0)  # Indeterminate
        self._thinking_bar.setFixedHeight(3)
        self._thinking_bar.setStyleSheet(
            "QProgressBar { border:none; background:#1a1a2e; } "
            "QProgressBar::chunk { background:#007acc; }"
        )
        self._thinking_bar.hide()
        root_layout.addWidget(self._thinking_bar)

        # Quick action buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(4)
        for label, action in [
            ("📖 Story", "generate_story"),
            ("🎬 Scene", "suggest_scene"),
            ("🎨 Character", "suggest_character"),
            ("💡 Ideas", "brainstorm"),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "QPushButton { background:#252535; border:1px solid #444; border-radius:4px; "
                "color:#ccc; font-size:10px; padding: 0 6px; } "
                "QPushButton:hover { background:#2f2f4f; }"
            )
            btn.clicked.connect(lambda checked=False, a=action: self._quick_action(a))
            quick_layout.addWidget(btn)
        root_layout.addLayout(quick_layout)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask the AI anything...")
        self._input.setStyleSheet(
            "QLineEdit { background:#252535; border:1px solid #444; border-radius:6px; "
            "color:#e0e0e0; padding: 6px 10px; font-size:12px; } "
            "QLineEdit:focus { border:1px solid #007acc; }"
        )
        self._input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self._input)

        self._send_btn = QPushButton("▶")
        self._send_btn.setFixedSize(32, 32)
        self._send_btn.setStyleSheet(
            "QPushButton { background:#007acc; border:none; border-radius:6px; color:white; "
            "font-size:14px; } QPushButton:hover { background:#0098ff; } "
            "QPushButton:disabled { background:#333; color:#555; }"
        )
        self._send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self._send_btn)

        root_layout.addLayout(input_layout)

    # ------------------------------------------------------------------
    # Event connections
    # ------------------------------------------------------------------

    def _connect_events(self):
        try:
            bus = registry.get(EventBus)
            bus.subscribe(Event.WORKSPACE_CHANGED, self._on_workspace_changed)
            bus.subscribe(Event.PROJECT_OPENED, self._on_project_opened)
            bus.subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)
            bus.subscribe(Event.AI_TASK_FAILED, self._on_ai_failed)
        except KeyError:
            logger.debug("AICopilotDock: EventBus not yet available.")

        self._response_ready.connect(self._display_assistant_response)

    def _on_workspace_changed(self, workspace_name: str):
        self._active_workspace = workspace_name
        self._context_label.setText(f"Context: {workspace_name}")
        self._update_context()

    def _on_project_opened(self, path: str):
        import os
        project_name = os.path.basename(path)
        self._context = f"Project: {project_name}, Workspace: {self._active_workspace}"
        self._context_label.setText(f"Context: {project_name} › {self._active_workspace}")

    def _update_context(self):
        self._context = f"Active workspace: {self._active_workspace}"

    # ------------------------------------------------------------------
    # Chat logic
    # ------------------------------------------------------------------

    def _send_message(self):
        text = self._input.text().strip()
        if not text:
            return

        self._input.clear()
        self._add_user_message(text)
        self._set_thinking(True)

        try:
            from src.core.ai import ZanimeAIAPI
            api = registry.get(ZanimeAIAPI)
            self._pending_task_id = api.chat(text, self._context, {})
        except (KeyError, Exception) as exc:
            logger.error("AICopilotDock: Failed to send message — %s", exc)
            self._set_thinking(False)
            self._add_system_message(
                "⚠ AI not available. Make sure Ollama is running (ollama serve)."
            )

    def _on_ai_completed(self, data: dict):
        if self._pending_task_id and data.get("id") == self._pending_task_id:
            self._pending_task_id = None
            result = data.get("result", {})
            text = result.get("text", str(result)) if isinstance(result, dict) else str(result)
            self._response_ready.emit(text)
            self._set_thinking(False)

    def _on_ai_failed(self, data: dict):
        if self._pending_task_id and data.get("id") == self._pending_task_id:
            self._pending_task_id = None
            self._set_thinking(False)
            self._add_system_message(f"⚠ Error: {data.get('error', 'Unknown error')}")

    def _quick_action(self, action: str):
        prompts = {
            "generate_story":    "Generate a complete anime story concept for my current project with interesting characters and a compelling plot twist.",
            "suggest_scene":     "Suggest 3 interesting scene ideas that would work well for the current story, with location, mood and character dynamics.",
            "suggest_character": "Create a detailed unique anime character concept with name, personality, backstory, and visual description.",
            "brainstorm":        "Give me 5 creative ideas to make my animation project more interesting and original.",
        }
        self._input.setText(prompts.get(action, ""))
        self._send_message()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _add_user_message(self, text: str):
        bubble = MessageBubble(text, role="user")
        self._chat_layout.addWidget(bubble)
        self._scroll_to_bottom()
        self._conversation.append({"role": "user", "text": text})

    def _display_assistant_response(self, text: str):
        bubble = MessageBubble(text, role="assistant")
        self._chat_layout.addWidget(bubble)
        self._scroll_to_bottom()
        self._conversation.append({"role": "assistant", "text": text})

    def _add_system_message(self, text: str):
        bubble = MessageBubble(text, role="system")
        self._chat_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _set_thinking(self, thinking: bool):
        self._thinking_bar.setVisible(thinking)
        self._send_btn.setEnabled(not thinking)
        self._input.setEnabled(not thinking)

    def _scroll_to_bottom(self):
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )
