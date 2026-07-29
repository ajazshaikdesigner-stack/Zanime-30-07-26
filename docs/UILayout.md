# UI Layout & Performance Guidelines

## Aesthetics
- **Dark Theme First**: ZANIME utilizes a professional dark theme mapped out in `src/ui/theme/palette.json`.
- **Decluttered**: Do not render buttons that aren't necessary. Rely on context menus and shortcut chords (`ShortcutManager`).

## Performance Limits
Target hardware: AMD Ryzen 5 5600H, AMD Radeon RX6500M 4GB, 16GB RAM.
- **No pure CUDA**: Since target is AMD, rely on PySide6 hardware acceleration.
- **Memory**: The UI framework pre-allocates docks at boot but does not load asset data into memory until the Asset Browser explicitly requests it.
