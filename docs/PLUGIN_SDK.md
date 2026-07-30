# ZANIME Plugin SDK & Developer Guide

## Overview

The **ZANIME Plugin SDK** allows third-party developers to extend ZANIME Studio with custom VFX filters, node types, AI providers, tools, and exporters.

---

## 1. Plugin Directory Structure

Plugins are loaded from the `./plugins/` directory or project-specific plugin folders.

```
plugins/
  ├── my_vfx_plugin.py
  └── my_node_pack/
      ├── __init__.py
      └── nodes.py
```

---

## 2. Plugin Metadata & Registration

Every plugin file MUST define a `PLUGIN_METADATA` dictionary and an `initialize()` function.

```python
"""
Sample Custom VFX Plugin for ZANIME Studio
"""
import logging

logger = logging.getLogger(__name__)

PLUGIN_METADATA = {
    "name": "My Custom VFX Pack",
    "version": "1.0.0",
    "author": "Animation Studio Lab",
    "description": "Adds vintage CRT scanline and vignette effects.",
    "category": "VFX",
    "signature": "VERIFIED",   # Optional signature for enterprise mode
}

def initialize():
    """Plugin Lifecycle Hook — Executed on ZANIME startup."""
    logger.info("Initializing My Custom VFX Pack...")
    
    # Register custom VFX or Nodes into ZANIME ServiceRegistry
    from src.core.services.vfx_engine import VFXEngine
    from src.core.services.service_registry import registry
    
    # Access runtime services safely
    try:
        vfx = registry.get(VFXEngine)
        logger.info("Registered custom plugin effects into VFX Engine.")
    except Exception as e:
        logger.error("Failed to register plugin: %s", e)
```

---

## 3. Creating Custom Node Types for Node Graph

To register custom nodes into the Node Graph workspace:

```python
from src.models.node_graph_model import NODE_CATALOG

MY_CUSTOM_NODE = {
    "type_id": "custom_sepia_filter",
    "name": "Sepia Tone Filter",
    "category": "Image",
    "inputs": [("image", "in_image", "image"), ("number", "strength", "number")],
    "outputs": [("image", "out_image", "image")]
}

def initialize():
    NODE_CATALOG.append(MY_CUSTOM_NODE)
```

---

## 4. Security & Digital Signatures

For commercial distribution on the ZANIME Plugin Marketplace:
1. Compute SHA-256 HMAC of `"{name}:{version}:SECRET_SALT_2026"`.
2. Include the resulting 16-character hex digest as `signature` in `PLUGIN_METADATA`.
3. Unsigned plugins will trigger an informational notice on load.

---

## 5. Verification Checklist

- [x] Defines `PLUGIN_METADATA` dict with `name`, `version`, `author`
- [x] Defines top-level `initialize()` function
- [x] Contains no blocking loops or synchronous network calls on main UI thread
- [x] Passes AST security audit (no unauthorized file deletion or system calls)
