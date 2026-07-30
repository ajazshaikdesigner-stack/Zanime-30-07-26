# ZANIME 1.0 — Public API Documentation

## 1. Core API (`ZanimeAIAPI`)

The central entry point for AI, story, character, storyboard, and background generation.

```python
from src.core.services.service_registry import registry
from src.core.ai import ZanimeAIAPI

api = registry.get(ZanimeAIAPI)
```

### Methods

#### `generate_story(prompt: str, options: dict) -> str`
Queues asynchronous story generation via Ollama LLM.
- **Returns**: `task_id` (string UUID)

#### `generate_scene_breakdown(story_text: str, options: dict) -> str`
Breaks screenplay text into a JSON scene list.

#### `generate_storyboard_plan(scene_desc: str, options: dict) -> str`
Generates JSON shot plan from scene description.

#### `generate_character_image(prompt: str, options: dict) -> str`
Generates anime character portrait or turnaround via ComfyUI.

#### `generate_background(prompt: str, options: dict) -> str`
Generates 1344×768 landscape background environment image.

---

## 2. Event Bus API (`EventBus`)

Decoupled publish-subscribe event system across all managers and UI docks.

```python
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event

bus = registry.get(EventBus)

# Subscribe to event
def on_camera_switched(data: dict):
    print(f"Camera switched to {data['camera_name']}")

bus.subscribe(Event.CAMERA_SWITCHED, on_camera_switched)

# Publish event
bus.publish(Event.CAMERA_SWITCHED, {"camera_uuid": "123", "camera_name": "Wide"})
```

---

## 3. Service Registry (`ServiceRegistry`)

Global dependency injection registry for singleton services and factories.

```python
from src.core.services.service_registry import registry

# Register a service instance
registry.register(MyService, my_instance)

# Register factory
registry.register_factory(MyService, lambda: MyService())

# Retrieve service
service = registry.get(MyService)
```
