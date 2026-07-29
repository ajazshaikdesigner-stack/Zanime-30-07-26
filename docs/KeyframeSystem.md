# Keyframe System

Zanime implements a robust, modular keyframe architecture. 

## Supported Properties
- `x`: Horizontal translation (pixels)
- `y`: Vertical translation (pixels)
- `scale_x`: Horizontal scale factor
- `scale_y`: Vertical scale factor
- `rotation`: Degrees of rotation
- `opacity`: Alpha blend (0.0 to 1.0)
- `expression`: State trigger for 2D facial textures

## Interpolation Modes
- **Hold**: Snap directly to the next value when the frame is reached. Perfect for lip-sync and 2D expressions.
- **Linear**: Constant rate of change between two values.
- **Bezier**: Smooth easing in and out using defined bezier curve handles (future implementation).
