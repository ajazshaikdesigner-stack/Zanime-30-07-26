"""
AI API Facades - Provides unified access for Studio modules.
"""
import logging
from typing import Dict, Any
from .manager import AIManager

logger = logging.getLogger(__name__)

class ZanimeAIAPI:
    def __init__(self, ai_manager: AIManager):
        self.ai = ai_manager
        
    def generate_story(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for StoryAI"""
        logger.info(f"API: Story generation requested: {prompt}")
        return self.ai.execute_task("llm", "llama3:8b", prompt, params, priority=1)
        
    def generate_script(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for ScriptAI"""
        logger.info(f"API: Script generation requested: {prompt}")
        return self.ai.execute_task("llm", "llama3:8b", prompt, params, priority=1)
        
    def generate_storyboard(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for StoryboardAI"""
        logger.info(f"API: Storyboard generation requested: {prompt}")
        return self.ai.execute_task("diffusion", "zanime_sdxl", prompt, params, priority=2)
        
    def generate_animation(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for Animation AI"""
        logger.info(f"API: Animation generation requested: {prompt}")
        return self.ai.execute_task("diffusion", "zanime_sdxl", prompt, params, priority=2)
        
    def generate_camera_plan(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for Camera AI"""
        logger.info(f"API: Camera plan generation requested: {prompt}")
        return self.ai.execute_task("llm", "llama3:8b", prompt, params, priority=1)
        
    def generate_voice(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for Voice AI"""
        logger.info(f"API: Voice generation requested: {prompt}")
        return self.ai.execute_task("audio", "tts_model", prompt, params, priority=2)
        
    def generate_lipsync(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for Lip Sync AI"""
        logger.info(f"API: Lip Sync generation requested: {prompt}")
        return self.ai.execute_task("audio", "viseme_model", prompt, params, priority=2)
        
    def generate_character_image(self, prompt: str, params: Dict[str, Any]) -> str:
        """Facade for CharacterAI"""
        logger.info(f"API: Character generation requested: {prompt}")
        return self.ai.execute_task("diffusion", "zanime_sdxl", prompt, params, priority=2)
        
    def generate_voice(self, text: str, params: Dict[str, Any]) -> str:
        """Facade for VoiceAI"""
        logger.info(f"API: TTS requested: {text}")
        return self.ai.execute_task("tts", "piper_voice", text, params, priority=1)
        
    def transcribe_audio(self, audio_path: str, params: Dict[str, Any]) -> str:
        """Facade for MusicAI/VoiceAI STT"""
        logger.info(f"API: STT requested for {audio_path}")
        return self.ai.execute_task("stt", "whisper_base", audio_path, params, priority=1)
