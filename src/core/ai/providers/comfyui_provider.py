"""
ComfyUI Image Generation Provider.

Connects to a locally running ComfyUI server via HTTP API.
Default endpoint: http://localhost:8188
Override via config key: ai_settings.comfyui_url

ComfyUI uses a workflow-based JSON API. We ship a built-in
txt2img workflow and allow custom workflow injection via params.
"""

import json
import logging
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)

_COMFYUI_DEFAULT_URL = "http://localhost:8188"
_CLIENT_ID = str(uuid.uuid4())  # Persistent session ID for this app run


# ---------------------------------------------------------------------------
# Built-in minimal txt2img workflow for SDXL-style models
# ---------------------------------------------------------------------------
def _build_txt2img_workflow(
    positive: str,
    negative: str,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    seed: int,
    model_checkpoint: str,
) -> dict:
    """Return a ComfyUI workflow dict for basic txt2img."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": cfg,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "karras",
                "seed": seed,
                "steps": steps,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model_checkpoint},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": positive},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "zanime_gen", "images": ["8", 0]},
        },
    }


class ComfyUIProvider(AIBaseProvider):
    """
    ComfyUI-backed image generation provider.

    execute() params keys:
      negative_prompt (str)  — negative conditioning
      width  (int)           — image width  (default 512)
      height (int)           — image height (default 768)
      steps  (int)           — sampler steps (default 25)
      cfg    (float)         — CFG scale (default 7.0)
      seed   (int)           — generation seed (-1 = random)
      workflow (dict)        — override the entire ComfyUI workflow
      output_dir (str)       — where to save the result image locally
    """

    def __init__(self):
        super().__init__()
        self._base_url = _COMFYUI_DEFAULT_URL
        self._model_checkpoint = "v1-5-pruned-emaonly.ckpt"

    # ------------------------------------------------------------------
    # AIBaseProvider interface
    # ------------------------------------------------------------------

    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        self._base_url = config.get("comfyui_url", _COMFYUI_DEFAULT_URL).rstrip("/")
        self._model_checkpoint = model_name or self._model_checkpoint

        try:
            url = f"{self._base_url}/system_stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                stats = json.loads(resp.read().decode())
            vram_free = stats.get("system", {}).get("vram_free", 0) / (1024 ** 3)
            logger.info(
                "ComfyUIProvider: Connected. VRAM free: %.2f GB. Model: %s",
                vram_free,
                self._model_checkpoint,
            )
            self.is_loaded = True
            return True
        except urllib.error.URLError as exc:
            logger.error("ComfyUIProvider: Cannot reach ComfyUI at %s — %s", self._base_url, exc)
            self.is_loaded = False
            return False
        except Exception:
            logger.exception("ComfyUIProvider: Unexpected error during load.")
            self.is_loaded = False
            return False

    def unload(self) -> None:
        self.is_loaded = False
        logger.info("ComfyUIProvider: Unloaded.")

    def execute(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Queue a ComfyUI workflow and poll until complete. Returns output image path."""
        if not self.is_loaded:
            raise RuntimeError("ComfyUIProvider: Not loaded. Call load() first.")

        import os
        import random

        negative = parameters.get("negative_prompt", "ugly, bad anatomy, blurry, low quality")
        width    = parameters.get("width", 512)
        height   = parameters.get("height", 768)
        steps    = parameters.get("steps", 25)
        cfg      = parameters.get("cfg", 7.0)
        seed     = parameters.get("seed", -1)
        output_dir = parameters.get("output_dir", os.path.expanduser("~/.zanime/generated"))

        if seed == -1:
            seed = random.randint(0, 2**31 - 1)

        # Allow full workflow override for advanced users
        workflow = parameters.get(
            "workflow",
            _build_txt2img_workflow(
                positive=prompt,
                negative=negative,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                seed=seed,
                model_checkpoint=self._model_checkpoint,
            ),
        )

        prompt_id = self._queue_prompt(workflow)
        logger.info("ComfyUIProvider: Queued prompt_id=%s (seed=%d)", prompt_id, seed)

        # Poll history until job completes
        output_path = self._wait_for_result(prompt_id, output_dir, timeout=300)

        return {
            "image_path": output_path,
            "seed": seed,
            "model": self._model_checkpoint,
            "prompt_id": prompt_id,
        }

    def memory_footprint(self) -> int:
        # Typical SD 1.5 = ~2GB; SDXL = ~6GB
        if "xl" in self._model_checkpoint.lower():
            return 6000
        return 2000

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _queue_prompt(self, workflow: dict) -> str:
        """POST the workflow to ComfyUI and return the prompt_id."""
        payload = json.dumps({"prompt": workflow, "client_id": _CLIENT_ID}).encode()
        req = urllib.request.Request(
            f"{self._base_url}/prompt",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI did not return a prompt_id: {result}")
        return prompt_id

    def _wait_for_result(self, prompt_id: str, output_dir: str, timeout: int = 300) -> str:
        """Poll /history/{prompt_id} until images are ready, then download."""
        import os

        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                url = f"{self._base_url}/history/{prompt_id}"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    history = json.loads(resp.read().decode())

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for _node_id, node_out in outputs.items():
                        images = node_out.get("images", [])
                        if images:
                            return self._download_image(images[0], output_dir)
            except urllib.error.URLError:
                pass  # Server may still be processing; keep polling

            time.sleep(2)

        raise TimeoutError(f"ComfyUI: Prompt {prompt_id} did not complete within {timeout}s.")

    def _download_image(self, image_info: dict, output_dir: str) -> str:
        """Download the generated image from ComfyUI /view endpoint."""
        import os

        filename = image_info.get("filename", "output.png")
        subfolder = image_info.get("subfolder", "")
        img_type  = image_info.get("type", "output")

        params = f"filename={filename}&subfolder={subfolder}&type={img_type}"
        url = f"{self._base_url}/view?{params}"

        os.makedirs(output_dir, exist_ok=True)
        local_path = os.path.join(output_dir, filename)

        with urllib.request.urlopen(url, timeout=30) as resp:
            with open(local_path, "wb") as f:
                f.write(resp.read())

        logger.info("ComfyUIProvider: Image saved to %s", local_path)
        return local_path
