# Lip Sync System (Visemes)

To animate 2D characters, audio data must be translated into visual shapes. Zanime uses a **Viseme** system.

## Viseme Mapping
When `generate_lipsync()` is called via the AI API, the backend analyzes the generated audio wave and maps it to a list of `VisemeData` objects.

A `VisemeData` object strictly assigns a mouth shape (e.g., "A", "O", "Closed") to a precise integer `frame`. The renderer later reads this array to swap out the character's facial textures on the fly.
