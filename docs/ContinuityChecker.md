# Continuity Checker

Before a Storyboard can be passed into the Scene Composer/Animation layers, it must pass the `ContinuityChecker`.

## Validations
1. **Timeline Errors**: Ensure no Shot has a duration of `<= 0.0` seconds, which would crash the renderer.
2. **Missing Environments**: A Scene *must* be bound to an Environment UUID, or else the actors have nowhere to stand.
3. **Outfit Consistency**: (Future) Warns if a character's outfit changes between shots within the same continuous scene.
