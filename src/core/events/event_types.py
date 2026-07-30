"""
Constants defining event types for the ZANIME EventBus.
"""

from enum import Enum, auto


class Event(Enum):
    # Lifecycle
    APP_STARTED = auto()
    APP_SHUTDOWN = auto()

    # Projects
    PROJECT_OPENED = auto()
    PROJECT_SAVED = auto()
    PROJECT_CLOSED = auto()

    # Workspace
    WORKSPACE_CHANGED = auto()

    # State
    SELECTION_CHANGED = auto()
    THEME_CHANGED = auto()

    # Actions
    UNDO_EXECUTED = auto()
    REDO_EXECUTED = auto()

    # AI System
    AI_TASK_STARTED = auto()
    AI_TASK_COMPLETED = auto()
    AI_TASK_FAILED = auto()
    AI_TASK_PROGRESS = auto()
    AI_MODEL_LOADED = auto()
    AI_MODEL_UNLOADED = auto()
