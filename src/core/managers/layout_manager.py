"""
Layout Manager for saving and restoring window dock states per workspace.
"""
import logging
from PySide6.QtCore import QByteArray
from src.core.managers.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)

class LayoutManager:
    def __init__(self, config_manager: ConfigurationManager, main_window):
        self.config_manager = config_manager
        self.main_window = main_window

    def save_layout(self, workspace_name: str) -> None:
        """Saves the current main window state to the user config."""
        if not self.main_window:
            return
            
        state = self.main_window.saveState()
        # Convert QByteArray to base64 string for JSON serialization
        state_b64 = state.toBase64().data().decode('utf-8')
        
        layouts = self.config_manager.get("layouts", {})
        layouts[workspace_name] = state_b64
        self.config_manager.set_user("layouts", layouts)
        logger.debug(f"Saved layout for workspace: {workspace_name}")

    def restore_layout(self, workspace_name: str) -> bool:
        """Restores the main window state from the user config."""
        if not self.main_window:
            return False
            
        layouts = self.config_manager.get("layouts", {})
        if workspace_name in layouts:
            state_b64 = layouts[workspace_name]
            state = QByteArray.fromBase64(state_b64.encode('utf-8'))
            restored = self.main_window.restoreState(state)
            if restored:
                logger.debug(f"Restored layout for workspace: {workspace_name}")
                return True
            else:
                logger.warning(f"Failed to restore layout for workspace: {workspace_name}")
        return False
