"""
Constants defining event types for the ZANIME EventBus.
"""

from enum import Enum, auto


class Event(Enum):
    # Lifecycle
    APP_STARTED = auto()
    APP_SHUTDOWN = auto()
    HEALTH_CHECK_COMPLETED = auto()

    # Projects
    PROJECT_OPENED = auto()
    PROJECT_SAVED = auto()
    PROJECT_CLOSED = auto()
    PROJECT_RECOVERED = auto()

    # Workspace
    WORKSPACE_CHANGED = auto()

    # State
    SELECTION_CHANGED = auto()
    THEME_CHANGED = auto()
    TOOL_CHANGED = auto()

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
    # AI History
    AI_HISTORY_ENTRY_ADDED = auto()
    # Model downloads
    AI_MODEL_DOWNLOAD_STARTED = auto()
    AI_MODEL_DOWNLOAD_PROGRESS = auto()
    AI_MODEL_DOWNLOAD_COMPLETE = auto()
    AI_MODEL_DOWNLOAD_FAILED = auto()
    # Copilot
    AI_COPILOT_MESSAGE = auto()
    # Consistency
    AI_CONSISTENCY_UPDATED = auto()

    # Camera System
    CAMERA_SWITCHED = auto()
    CAMERA_KEYFRAME_ADDED = auto()
    CAMERA_SWITCH_RECORDED = auto()

    # Timeline System
    TIMELINE_MARKER_ADDED = auto()
    TIMELINE_TRACK_ADDED = auto()
    TIMELINE_CLIP_MOVED = auto()

    # Node Graph
    NODE_GRAPH_EXECUTED = auto()
    NODE_CREATED = auto()

    # VFX & Compositing
    VFX_EFFECT_APPLIED = auto()
    COMPOSITING_LAYER_CHANGED = auto()

    # Render & Audio
    RENDER_JOB_QUEUED = auto()
    RENDER_FRAME_COMPLETED = auto()
    AUDIO_TRACK_MUTED = auto()

