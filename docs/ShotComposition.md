# Shot Composition & Analytics

To guarantee professional cinematic language, the `ShotAnalyzer` continuously validates the timeline for pacing errors.

## Pacing & Transitions
1. **Rapid Cuts**: A cut lasting fewer than 0.5 seconds (e.g. 12 frames at 24fps) will trigger a warning, as overly rapid cuts cause strobe effects and disorientation in standard anime.
2. **Custom Transitions**: Undefined transitions are flagged to ensure the renderer knows exactly how to bridge clips (e.g., Fade, Cut, Dissolve).

By keeping the camera logic strictly separated from Character Animation, directors can re-frame entire scenes without re-animating a single sprite.
