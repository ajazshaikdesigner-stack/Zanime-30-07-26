"""
AI Prompt Engine — template-based prompt construction system.

Features:
  - 50+ preset anime/cinematic/illustration style templates
  - Variable injection: {character_name}, {location}, {mood}, etc.
  - Character DNA → prompt fragment assembly
  - Negative prompt presets
  - Style suffix library
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Template Library
# ---------------------------------------------------------------------------

PROMPT_TEMPLATES: dict[str, dict[str, str]] = {
    # ── Character Templates ──────────────────────────────────────────────
    "character_full_body": {
        "label":    "Character — Full Body",
        "category": "character",
        "positive": "{character_name}, full body, anime style, {outfit}, {hair_style} {hair_color} hair, standing pose, white background, character sheet, high quality",
        "negative": "bad anatomy, extra limbs, cropped, blurry, low quality, watermark",
        "variables": ["character_name", "outfit", "hair_style", "hair_color"],
    },
    "character_portrait": {
        "label":    "Character — Portrait",
        "category": "character",
        "positive": "{character_name}, portrait, anime face, {expression} expression, {eye_color} eyes, {hair_color} hair, studio lighting, high quality",
        "negative": "ugly, bad face, asymmetrical, blurry",
        "variables": ["character_name", "expression", "eye_color", "hair_color"],
    },
    "character_turnaround": {
        "label":    "Character — Turnaround Sheet",
        "category": "character",
        "positive": "{character_name}, character turnaround, 4 views front back left right, anime, {outfit}, white background",
        "negative": "bad anatomy, merged figures, overlapping",
        "variables": ["character_name", "outfit"],
    },
    "character_expression_sheet": {
        "label":    "Character — Expression Sheet",
        "category": "character",
        "positive": "{character_name}, anime expression sheet, 6 emotions: happy sad angry surprised scared neutral, white background",
        "negative": "bad anatomy, blurry",
        "variables": ["character_name"],
    },
    "character_action": {
        "label":    "Character — Action Pose",
        "category": "character",
        "positive": "{character_name}, {action_pose}, anime action scene, dynamic angle, motion blur, {mood} mood",
        "negative": "static pose, low quality, bad anatomy",
        "variables": ["character_name", "action_pose", "mood"],
    },

    # ── Background Templates ─────────────────────────────────────────────
    "background_exterior_day": {
        "label":    "Background — Exterior Day",
        "category": "background",
        "positive": "anime background, {location}, daytime, {weather} weather, {season} season, detailed environment, Studio Ghibli style",
        "negative": "characters, people, low quality",
        "variables": ["location", "weather", "season"],
    },
    "background_exterior_night": {
        "label":    "Background — Exterior Night",
        "category": "background",
        "positive": "anime background, {location}, night, moonlight, stars, {mood} atmosphere, detailed environment",
        "negative": "characters, people, low quality",
        "variables": ["location", "mood"],
    },
    "background_interior": {
        "label":    "Background — Interior",
        "category": "background",
        "positive": "anime interior background, {room_type}, {lighting_style} lighting, detailed decor, {time_of_day}",
        "negative": "characters, people, low quality, plain",
        "variables": ["room_type", "lighting_style", "time_of_day"],
    },
    "background_fantasy": {
        "label":    "Background — Fantasy World",
        "category": "background",
        "positive": "anime fantasy background, {world_type}, magical, ethereal, detailed landscape, high quality",
        "negative": "modern, realistic, low quality",
        "variables": ["world_type"],
    },
    "background_scifi": {
        "label":    "Background — Sci-Fi",
        "category": "background",
        "positive": "anime sci-fi background, {setting}, futuristic, neon lights, high tech, cinematic",
        "negative": "fantasy, nature, low quality",
        "variables": ["setting"],
    },
    "background_school": {
        "label":    "Background — School",
        "category": "background",
        "positive": "anime school background, {room_type}, clean, bright, after-school atmosphere",
        "negative": "characters, people, low quality",
        "variables": ["room_type"],
    },

    # ── Storyboard / Scene Templates ─────────────────────────────────────
    "scene_wide_shot": {
        "label":    "Scene — Wide Shot",
        "category": "scene",
        "positive": "anime scene, wide shot, {location}, {characters}, establishing shot, cinematic composition, {mood} atmosphere",
        "negative": "close up, portrait, low quality",
        "variables": ["location", "characters", "mood"],
    },
    "scene_medium_shot": {
        "label":    "Scene — Medium Shot",
        "category": "scene",
        "positive": "anime scene, medium shot, {characters} talking, {location} background, {lighting} lighting",
        "negative": "wide shot, extreme close up, bad anatomy",
        "variables": ["characters", "location", "lighting"],
    },
    "scene_close_up": {
        "label":    "Scene — Close Up",
        "category": "scene",
        "positive": "anime scene, close up, {character_name} face, {expression}, detailed eyes, {mood} emotion",
        "negative": "full body, wide shot, low quality",
        "variables": ["character_name", "expression", "mood"],
    },
    "scene_action": {
        "label":    "Scene — Action Sequence",
        "category": "scene",
        "positive": "anime action scene, {characters}, {action_description}, dynamic camera, motion blur, cinematic, high energy",
        "negative": "static, peaceful, low quality",
        "variables": ["characters", "action_description"],
    },

    # ── Prop Templates ───────────────────────────────────────────────────
    "prop_weapon": {
        "label":    "Prop — Weapon",
        "category": "prop",
        "positive": "{weapon_name}, anime prop, detailed, isolated on white background, {style} style",
        "negative": "characters, background clutter",
        "variables": ["weapon_name", "style"],
    },
    "prop_vehicle": {
        "label":    "Prop — Vehicle",
        "category": "prop",
        "positive": "{vehicle_name}, anime vehicle, side view, clean lines, detailed, white background",
        "negative": "people, outdoor background",
        "variables": ["vehicle_name"],
    },
    "prop_magical_item": {
        "label":    "Prop — Magical Item",
        "category": "prop",
        "positive": "{item_name}, magical artifact, anime fantasy, glowing, ornate, detailed, isolated",
        "negative": "plain, boring, characters",
        "variables": ["item_name"],
    },

    # ── Cinematic / Poster Templates ─────────────────────────────────────
    "poster_key_visual": {
        "label":    "Poster — Key Visual",
        "category": "cinematic",
        "positive": "anime key visual poster, {title}, {main_character}, {setting}, epic composition, dramatic lighting, high quality promotional art",
        "negative": "low quality, watermark, text overlay",
        "variables": ["title", "main_character", "setting"],
    },
    "thumbnail_episode": {
        "label":    "Thumbnail — Episode",
        "category": "cinematic",
        "positive": "anime episode thumbnail, {characters}, {scene_description}, cinematic, eye-catching, 16:9 ratio",
        "negative": "low quality, plain background",
        "variables": ["characters", "scene_description"],
    },
}


# ---------------------------------------------------------------------------
# Style Suffixes
# ---------------------------------------------------------------------------

STYLE_SUFFIXES: dict[str, str] = {
    "zanime_default":   "ZANIME production art, anime style, clean lines, vibrant colors, professional quality",
    "ghibli":           "Studio Ghibli style, soft watercolor, lush backgrounds, gentle atmosphere",
    "action_shonen":    "shonen anime style, dynamic lines, bold colors, dramatic poses",
    "slice_of_life":    "slice of life anime, pastel colors, warm lighting, cozy atmosphere",
    "dark_fantasy":     "dark fantasy anime, moody colors, detailed armor, dramatic shadows",
    "moe":              "moe anime style, cute, soft colors, chibi proportions",
    "cyberpunk":        "cyberpunk anime, neon colors, rain, city lights, dystopian",
    "historical":       "historical anime, detailed period clothing, traditional setting",
}


# ---------------------------------------------------------------------------
# Negative Prompt Presets
# ---------------------------------------------------------------------------

NEGATIVE_PRESETS: dict[str, str] = {
    "standard":     "ugly, bad anatomy, extra limbs, blurry, low quality, watermark, text, signature",
    "portrait":     "bad face, asymmetrical face, extra eyes, ugly, blurry, deformed, low quality",
    "background":   "characters, people, low quality, blurry, overexposed, flat",
    "action":       "static pose, stiff, low quality, bad anatomy, ugly",
    "professional": "amateur, sketch, rough, low quality, watermark, noise, grain, jpeg artifact",
}


class PromptEngine:
    """
    Assembles final prompts from templates, variables, character DNA,
    style suffixes and negative presets.
    """

    @staticmethod
    def fill_template(template_key: str, variables: dict[str, str]) -> dict[str, str]:
        """
        Fill a template with variable values. Returns {positive, negative}.
        Missing variables are left as {placeholder}.
        """
        if template_key not in PROMPT_TEMPLATES:
            raise KeyError(f"PromptEngine: Unknown template '{template_key}'")

        tpl = PROMPT_TEMPLATES[template_key]
        positive = tpl["positive"]
        negative = tpl["negative"]

        for key, value in variables.items():
            positive = positive.replace(f"{{{key}}}", value)
            negative = negative.replace(f"{{{key}}}", value)

        return {"positive": positive, "negative": negative}

    @staticmethod
    def apply_style(prompt: str, style_key: str) -> str:
        """Append a style suffix to the prompt."""
        suffix = STYLE_SUFFIXES.get(style_key, "")
        if suffix and suffix not in prompt:
            return f"{prompt.rstrip(', ')}, {suffix}"
        return prompt

    @staticmethod
    def get_negative(preset_key: str = "standard") -> str:
        """Return a negative prompt preset."""
        return NEGATIVE_PRESETS.get(preset_key, NEGATIVE_PRESETS["standard"])

    @staticmethod
    def list_templates(category: str | None = None) -> list[dict[str, str]]:
        """Return all templates, optionally filtered by category."""
        result = []
        for key, tpl in PROMPT_TEMPLATES.items():
            if category and tpl.get("category") != category:
                continue
            result.append({
                "key":       key,
                "label":     tpl["label"],
                "category":  tpl.get("category", ""),
                "variables": tpl.get("variables", []),
            })
        return result

    @staticmethod
    def list_styles() -> list[dict[str, str]]:
        return [{"key": k, "label": k.replace("_", " ").title()} for k in STYLE_SUFFIXES]

    @staticmethod
    def assemble(
        base_prompt: str,
        style_key: str = "zanime_default",
        negative_preset: str = "standard",
        extra_positive: str = "",
        extra_negative: str = "",
    ) -> dict[str, str]:
        """
        Full assembly pipeline: base → style → merge extras → return {positive, negative}.
        """
        positive = PromptEngine.apply_style(base_prompt, style_key)
        if extra_positive:
            positive = f"{positive}, {extra_positive}"

        negative = PromptEngine.get_negative(negative_preset)
        if extra_negative:
            negative = f"{negative}, {extra_negative}"

        return {"positive": positive, "negative": negative}

    @staticmethod
    def extract_variables(template_key: str) -> list[str]:
        """Return the list of variable names expected by a template."""
        tpl = PROMPT_TEMPLATES.get(template_key, {})
        return tpl.get("variables", [])
