# Theme Engine

ZANIME requires a commercial-grade, polished aesthetic. Relying solely on raw QSS is brittle. We will implement a robust Theme Engine.

## Responsibilities
- **QSS Generation**: Combine base QSS files with dynamic color palettes.
- **Color Palette Injection**: Read a `palette.json` and replace CSS variables (e.g., `@primary_color`) in the raw QSS before applying it to the application.
- **Theme Switching**: Support dynamic switching between Dark Theme (default) and Light Theme without restarting the app.
- **DPI Scaling**: Calculate logical DPI and adjust fonts and paddings dynamically to support high-res Windows 11 displays.

## Font & DPI Scaling Strategy
- Use OS-native fonts initially (`Segoe UI` on Windows), falling back to bundled fonts if specific typography is requested.
- Base font size: 10pt.
- Scale margins, padding, and icon sizes by `app.screens()[0].logicalDotsPerInch() / 96.0`.

## Icon Theme
- Icons must be resolution-independent.
- Initial implementation will use bundled SVG icons (tinted dynamically by the Theme Engine to match the active text color).
