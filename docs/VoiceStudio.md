# Voice & Dialogue Studio

The Voice Studio orchestrates text-to-speech generation and lip-sync mapping along an audio timeline.

## Data Structures
- **VoiceProfile**: Defines a character's vocal traits (e.g. `pitch`, `speed`, `gender`, `age_group`, and `accent`).
- **DialogueClip**: A single audio block storing the original `text`, intended `emotion`, `volume`, and `audio_path`.
- **VisemeData**: Represents a facial mouth shape triggered at a specific `frame`.
- **VoiceTimeline**: A multi-track timeline managing overlapping audio layers.

## I/O
The studio can export a strictly structured `Dialogue Package` (JSON). This structure maps Character UUIDs to their required audio file paths and exact start frames, which is heavily relied upon by the final Movie Renderer to compile the scene's master audio track.
