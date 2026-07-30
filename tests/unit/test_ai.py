from unittest.mock import MagicMock

from src.core.ai.manager import AIManager
from src.core.ai.task_queue import AITaskQueue
from src.core.events.event_bus import EventBus


def test_ai_manager_vram_limits():
    """Test that loading a new model unloads the previous to save VRAM."""
    bus = EventBus()
    config_mock = MagicMock()
    config_mock.get_user.return_value = "mock_path"

    manager = AIManager(bus, config_mock)
    manager.initialize()

    # Fake load LLM
    manager.providers["llm"].load = MagicMock(return_value=True)
    manager.providers["llm"].unload = MagicMock()

    # Fake load Diffusion
    manager.providers["diffusion"].load = MagicMock(return_value=True)
    manager.providers["diffusion"].unload = MagicMock()

    manager.execute_task("llm", "llama3:8b", "test prompt", {})
    assert manager.active_provider == "llm"

    # Executing diffusion should unload llm
    manager.execute_task("diffusion", "zanime_sdxl", "test prompt", {})
    assert manager.active_provider == "diffusion"
    manager.providers["llm"].unload.assert_called_once()


def test_task_queue_cancel():
    """Test task queue cancellation logic."""
    queue = AITaskQueue()
    provider_mock = MagicMock()

    task = queue.queue_job(provider_mock, "test", {})
    assert task.task_id in queue.active_tasks

    res = queue.cancel_job(task.task_id)
    assert res is True
    assert task.is_cancelled is True
