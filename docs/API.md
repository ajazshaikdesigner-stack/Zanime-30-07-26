# ZANIME API Reference

## EventBus
`src.core.events.event_bus.EventBus`
- `publish(event_type: Event, *args, **kwargs)`
- `subscribe(event_type: Event, callback: Callable)`
- `unsubscribe(event_type: Event, callback: Callable)`

## ProjectManager
`src.core.managers.project_manager.ProjectManager`
- `create_project(name: str, path: str)`
- `open_project(path: str)`
- `save_project()`

## CommandManager
`src.core.managers.command_manager.CommandManager`
- `execute(command: ICommand)`
- `undo()`
- `redo()`

## ThemeEngine
`src.core.managers.theme_engine.ThemeEngine`
- `apply_theme()`: Compiles and injects the active theme QSS.
