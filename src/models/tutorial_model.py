"""
Data models for the Tutorial and Interactive Learning System.
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class TutorialStep:
    step_id: int
    title: str
    instruction_text: str
    target_workspace: str # "Story", "Characters", "Renderer", etc.
    
@dataclass
class Achievement:
    id: str
    name: str
    description: str
    unlocked: bool = False
    
@dataclass
class TutorialProgress:
    current_step_index: int = 0
    is_first_launch: bool = True
    achievements: List[Achievement] = field(default_factory=list)
