"""
AI API Facades - Provides unified access for Studio modules.
"""

import logging
from typing import Any

from .manager import AIManager

logger = logging.getLogger(__name__)


class ZanimeAIAPI:
    def __init__(self, ai_manager: AIManager):
        self.ai = ai_manager

    # ------------------------------------------------------------------
    # Story / Script (LLM)
    # ------------------------------------------------------------------

    def generate_story(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a complete story from a premise."""
        logger.info("API: Story generation requested")
        full_prompt = (
            "You are a professional anime screenwriter. "
            f"Write a complete episode story for the following premise:\n\n{prompt}\n\n"
            "Include: Title, Tagline, Character list, Scene-by-scene breakdown, and full dialogue."
        )
        return self.ai.execute_task("llm", "llama3:8b", full_prompt, params, priority=1)

    def generate_script(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a screenplay-format script."""
        logger.info("API: Script generation requested")
        full_prompt = (
            "You are a professional anime screenwriter. "
            f"Write a properly formatted screenplay for:\n\n{prompt}\n\n"
            "Use scene headings (INT./EXT.), action lines, and CHARACTER: dialogue format."
        )
        return self.ai.execute_task("llm", "llama3:8b", full_prompt, params, priority=1)

    def generate_scene_breakdown(self, story_text: str, params: dict[str, Any]) -> str:
        """Break down a story into scenes with shot lists."""
        logger.info("API: Scene breakdown requested")
        full_prompt = (
            "You are an anime director. Analyze this story and produce a JSON scene breakdown.\n\n"
            f"STORY:\n{story_text[:3000]}\n\n"
            'For each scene output: {"scene_number": N, "name": "...", "location": "...", '
            '"characters": [...], "mood": "...", "shots": [{"type": "...", "description": "..."}]}'
        )
        return self.ai.execute_task("llm", "llama3:8b", full_prompt, params, priority=1)

    def expand_dialogue(self, scene_text: str, character: str, params: dict[str, Any]) -> str:
        """Expand or improve dialogue for a specific character in a scene."""
        logger.info("API: Dialogue expansion requested for %s", character)
        full_prompt = (
            f"Improve and expand the dialogue for character '{character}' in this scene, "
            f"keeping their personality consistent and natural:\n\n{scene_text}"
        )
        return self.ai.execute_task("llm", "llama3:8b", full_prompt, params, priority=1)

    def generate_storyboard_plan(self, scene_description: str, params: dict[str, Any]) -> str:
        """Generate a shot-by-shot storyboard plan from a scene description."""
        logger.info("API: Storyboard plan generation requested")
        full_prompt = (
            "You are an anime storyboard artist and director. "
            f"Create a detailed storyboard plan for this scene:\n\n{scene_description}\n\n"
            "For each shot output JSON: "
            '{"shot_number": N, "shot_type": "Wide/Medium/Close Up/ECU", '
            '"camera_movement": "Static/Pan/Tilt/Zoom", "duration_seconds": N, '
            '"description": "...", "dialogue": "...", "notes": "..."}'
        )
        return self.ai.execute_task("llm", "llama3:8b", full_prompt, params, priority=1)

    def chat(self, message: str, context: str, params: dict[str, Any]) -> str:
        """Global AI Copilot chat — context-aware assistant."""
        logger.info("API: Copilot chat message received")
        system = (
            "You are ZANIME Assistant, the AI creative co-pilot for ZANIME animation studio. "
            "Help the user create professional anime content. Be concise, creative and actionable. "
            f"Current project context: {context}"
        )
        return self.ai.execute_task(
            "llm", "llama3:8b", message, {**params, "system": system}, priority=2
        )

    # ------------------------------------------------------------------
    # Image Generation (ComfyUI)
    # ------------------------------------------------------------------

    def generate_character_image(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a character image via ComfyUI."""
        logger.info("API: Character image generation requested")
        return self.ai.execute_task("diffusion", "v1-5-pruned-emaonly.ckpt", prompt, params, priority=2)

    def generate_background(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a background image via ComfyUI."""
        logger.info("API: Background image generation requested")
        landscape_params = {**params, "width": 1344, "height": 768}
        return self.ai.execute_task("diffusion", "v1-5-pruned-emaonly.ckpt", prompt, landscape_params, priority=2)

    def generate_prop(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a prop/asset image via ComfyUI."""
        logger.info("API: Prop generation requested")
        return self.ai.execute_task("diffusion", "v1-5-pruned-emaonly.ckpt", prompt, params, priority=3)

    def generate_storyboard_panel(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate a single storyboard panel image."""
        logger.info("API: Storyboard panel generation requested")
        panel_params = {**params, "width": 768, "height": 432, "steps": 15}  # Faster for panels
        return self.ai.execute_task("diffusion", "v1-5-pruned-emaonly.ckpt", prompt, panel_params, priority=2)

    def upscale_image(self, image_path: str, params: dict[str, Any]) -> str:
        """Upscale an existing image via ComfyUI upscaler workflow."""
        logger.info("API: Image upscale requested for %s", image_path)
        upscale_params = {**params, "workflow_type": "upscale", "input_image": image_path}
        return self.ai.execute_task("diffusion", "RealESRGAN_x4plus.pth", image_path, upscale_params, priority=3)

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------

    def generate_voice(self, text: str, params: dict[str, Any]) -> str:
        """Synthesize speech from text via TTS provider."""
        logger.info("API: Voice synthesis requested (%d chars)", len(text))
        return self.ai.execute_task("tts", "xtts_v2", text, params, priority=2)

    def generate_lipsync(self, audio_path: str, params: dict[str, Any]) -> str:
        """Generate lip-sync data (word timestamps) from an audio file."""
        logger.info("API: Lip sync generation requested for %s", audio_path)
        return self.ai.execute_task("stt", "base", audio_path, params, priority=2)

    def transcribe_audio(self, audio_path: str, params: dict[str, Any]) -> str:
        """Transcribe audio to text via Whisper."""
        logger.info("API: STT requested for %s", audio_path)
        return self.ai.execute_task("stt", "base", audio_path, params, priority=1)

    def generate_music(self, prompt: str, params: dict[str, Any]) -> str:
        """Generate background music via MusicGen."""
        logger.info("API: Music generation requested")
        return self.ai.execute_task("music", "small", prompt, params, priority=3)

    def generate_sfx(self, description: str, params: dict[str, Any]) -> str:
        """Generate sound effects (currently routes to music provider with SFX mode)."""
        logger.info("API: SFX generation requested: %s", description)
        sfx_params = {**params, "mode": "sfx", "duration": params.get("duration", 3)}
        return self.ai.execute_task("music", "small", description, sfx_params, priority=3)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_active_provider(self) -> str | None:
        return self.ai.active_provider

    def is_ready(self) -> bool:
        return self.ai._is_initialized
