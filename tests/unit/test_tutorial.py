from src.core.managers.tutorial_manager import TutorialManager


def test_tutorial_manager():
    manager = TutorialManager()

    assert manager.progress.current_step_index == 0
    assert manager.get_current_step().target_workspace == "Story"

    # Test advancing
    manager.next_step()
    assert manager.progress.current_step_index == 1

    # Test achievement unlock triggered at step index 1
    ach = next(
        (a for a in manager.progress.achievements if a.id == "first_story"), None
    )
    assert ach.unlocked is True

    # Test previous
    manager.prev_step()
    assert manager.progress.current_step_index == 0
