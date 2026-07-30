"""
Data models for Visual Node Graph System — Phase 4.

Includes:
  - PortType (IMAGE, TEXT, AUDIO, NUMBER, FLOW)
  - NodePort (id, name, port_type, is_output, default_value)
  - NodeDefinition (type_id, name, category, input_ports, output_ports, color)
  - NodeModel (id, type_id, name, category, x, y, inputs, outputs, custom_data)
  - NodeConnection (from_node_id, from_port_id, to_node_id, to_port_id)
  - NodeGraphModel (nodes, connections, uuid)
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PortType(Enum):
    FLOW = "flow"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    NUMBER = "number"


PORT_COLORS = {
    PortType.FLOW.value: "#ffffff",
    PortType.IMAGE.value: "#ff922b",
    PortType.TEXT.value: "#4a9aff",
    PortType.AUDIO.value: "#51cf66",
    PortType.NUMBER.value: "#ffd43b",
}


@dataclass
class NodePort:
    port_id: str
    name: str
    port_type: str = PortType.FLOW.value
    is_output: bool = False
    value: Any = None


@dataclass
class NodeModel:
    type_id: str
    name: str
    category: str
    x: float = 0.0
    y: float = 0.0
    inputs: list[NodePort] = field(default_factory=list)
    outputs: list[NodePort] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class NodeConnection:
    from_node_id: str
    from_port_id: str
    to_node_id: str
    to_port_id: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class NodeGraphModel:
    name: str = "Main Graph"
    nodes: list[NodeModel] = field(default_factory=list)
    connections: list[NodeConnection] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_node(self, node: NodeModel) -> NodeModel:
        self.nodes.append(node)
        return node

    def remove_node(self, node_id: str):
        self.nodes = [n for n in self.nodes if n.uuid != node_id]
        self.connections = [c for c in self.connections if c.from_node_id != node_id and c.to_node_id != node_id]

    def connect(self, from_node: str, from_port: str, to_node: str, to_port: str) -> NodeConnection | None:
        # Check duplicate
        for c in self.connections:
            if c.to_node_id == to_node and c.to_port_id == to_port:
                self.connections.remove(c)  # replace single input connection
                break

        conn = NodeConnection(from_node_id=from_node, from_port_id=from_port, to_node_id=to_node, to_port_id=to_port)
        self.connections.append(conn)
        return conn

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "nodes": [
                {
                    "uuid": n.uuid,
                    "type_id": n.type_id,
                    "name": n.name,
                    "category": n.category,
                    "x": n.x,
                    "y": n.y,
                    "custom_data": n.custom_data,
                }
                for n in self.nodes
            ],
            "connections": [
                {
                    "uuid": c.uuid,
                    "from_node": c.from_node_id,
                    "from_port": c.from_port_id,
                    "to_node": c.to_node_id,
                    "to_port": c.to_port_id,
                }
                for c in self.connections
            ],
        }


# ---------------------------------------------------------------------------
# 20+ Node Type Definitions Catalog
# ---------------------------------------------------------------------------

NODE_CATALOG = [
    # Animation
    {"type_id": "anim_keyframe", "name": "Keyframe Generator", "category": "Animation", "inputs": [("flow", "in", "flow"), ("number", "start", "number"), ("number", "end", "number")], "outputs": [("flow", "out", "flow"), ("number", "value", "number")]},
    {"type_id": "anim_noise",    "name": "Perlin Noise",      "category": "Animation", "inputs": [("number", "frequency", "number")], "outputs": [("number", "noise", "number")]},
    {"type_id": "anim_easing",   "name": "Easing Curve",      "category": "Animation", "inputs": [("number", "t", "number")], "outputs": [("number", "eased_t", "number")]},
    # Image
    {"type_id": "img_load",      "name": "Image Loader",      "category": "Image",     "inputs": [], "outputs": [("image", "image", "image")]},
    {"type_id": "img_blur",      "name": "Gaussian Blur",     "category": "Image",     "inputs": [("image", "image", "image"), ("number", "radius", "number")], "outputs": [("image", "image", "image")]},
    {"type_id": "img_color",     "name": "Color Grade",       "category": "Image",     "inputs": [("image", "image", "image"), ("number", "contrast", "number")], "outputs": [("image", "image", "image")]},
    # Video
    {"type_id": "vid_input",     "name": "Video Source",      "category": "Video",     "inputs": [], "outputs": [("image", "frame", "image"), ("audio", "audio", "audio")]},
    {"type_id": "vid_composite", "name": "Layer Compositor",  "category": "Video",     "inputs": [("image", "bg", "image"), ("image", "fg", "image")], "outputs": [("image", "out", "image")]},
    # Audio
    {"type_id": "aud_input",     "name": "Audio Source",      "category": "Audio",     "inputs": [], "outputs": [("audio", "audio", "audio")]},
    {"type_id": "aud_volume",    "name": "Volume Gain",       "category": "Audio",     "inputs": [("audio", "audio", "audio"), ("number", "gain_db", "number")], "outputs": [("audio", "audio", "audio")]},
    # AI
    {"type_id": "ai_llm",        "name": "Ollama LLM",        "category": "AI",        "inputs": [("text", "prompt", "text")], "outputs": [("text", "response", "text")]},
    {"type_id": "ai_diffusion",  "name": "ComfyUI Generator", "category": "AI",        "inputs": [("text", "positive", "text"), ("text", "negative", "text")], "outputs": [("image", "image", "image")]},
    {"type_id": "ai_stt",        "name": "Whisper STT",       "category": "AI",        "inputs": [("audio", "audio", "audio")], "outputs": [("text", "transcript", "text")]},
    {"type_id": "ai_tts",        "name": "Piper TTS",         "category": "AI",        "inputs": [("text", "text", "text")], "outputs": [("audio", "audio", "audio")]},
    # Logic
    {"type_id": "logic_branch",  "name": "If / Else Branch",  "category": "Logic",     "inputs": [("flow", "in", "flow"), ("number", "condition", "number")], "outputs": [("flow", "true", "flow"), ("flow", "false", "flow")]},
    {"type_id": "logic_switch",  "name": "Value Switch",      "category": "Logic",     "inputs": [("number", "select", "number")], "outputs": [("text", "out", "text")]},
    # Math
    {"type_id": "math_add",      "name": "Add / Subtract",    "category": "Math",      "inputs": [("number", "a", "number"), ("number", "b", "number")], "outputs": [("number", "sum", "number")]},
    {"type_id": "math_mult",     "name": "Multiply / Divide", "category": "Math",      "inputs": [("number", "a", "number"), ("number", "b", "number")], "outputs": [("number", "product", "number")]},
    {"type_id": "math_clamp",    "name": "Range Clamp",       "category": "Math",      "inputs": [("number", "value", "number"), ("number", "min", "number"), ("number", "max", "number")], "outputs": [("number", "result", "number")]},
    # Render
    {"type_id": "render_output", "name": "Render Target",     "category": "Render",    "inputs": [("flow", "in", "flow"), ("image", "video_stream", "image"), ("audio", "audio_stream", "audio")], "outputs": []},
]


def create_node_from_definition(def_dict: dict, x: float = 0.0, y: float = 0.0) -> NodeModel:
    """Instantiate a NodeModel from catalog definition."""
    inputs = [NodePort(port_id=f"in_{p[1]}", name=p[1], port_type=p[2], is_output=False) for p in def_dict.get("inputs", [])]
    outputs = [NodePort(port_id=f"out_{p[1]}", name=p[1], port_type=p[2], is_output=True) for p in def_dict.get("outputs", [])]
    return NodeModel(
        type_id=def_dict["type_id"],
        name=def_dict["name"],
        category=def_dict["category"],
        x=x,
        y=y,
        inputs=inputs,
        outputs=outputs,
    )
