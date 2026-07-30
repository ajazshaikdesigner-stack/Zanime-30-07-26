"""
Inspectable interface for dynamic property generation.
"""

from abc import ABC, abstractmethod
from typing import Any

class IInspectable(ABC):
    @abstractmethod
    def get_properties(self) -> list[dict[str, Any]]:
        """
        Returns a list of property definitions.
        Example format:
        [
            {"id": "name", "label": "Name", "type": "string", "value": "MyObject"},
            {"id": "opacity", "label": "Opacity", "type": "int", "min": 0, "max": 100, "value": 50},
            {"id": "visible", "label": "Visible", "type": "bool", "value": True},
            {"id": "interp", "label": "Interpolation", "type": "enum", "options": ["Linear", "Ease In"], "value": "Linear"}
        ]
        """
        pass

    @abstractmethod
    def set_property(self, property_id: str, value: Any) -> None:
        """
        Called when the user modifies a property in the PropertiesDock.
        """
        pass
