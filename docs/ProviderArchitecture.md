# Provider Architecture

All AI backends implement `AIBaseProvider`.

## Required Methods
- `load(model, config)`
- `unload()`
- `execute(prompt, params)`
- `memory_footprint()`

## Current Providers
- **OllamaProvider** (LLM)
- **DiffusersProvider** (Images)
- **WhisperProvider** (STT)
- **PiperProvider** (TTS)
