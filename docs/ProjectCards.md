# Project Cards

`ProjectCard` is a custom PySide6 `QFrame` built for the Welcome Screen.

## Features
- **Hover Transitions**: Highlight borders and background shifts indicate interactivity.
- **Focus Policy**: Standardized to `Qt.StrongFocus`, allowing users to `Tab` through recent projects.
- **Key Events**: Listens for `Enter` or `Space` to execute the project load, supporting mouseless workflows.
- **Data Encapsulation**: Each card holds a dictionary of `project_data` which it emits via a custom `clicked(dict)` signal.
