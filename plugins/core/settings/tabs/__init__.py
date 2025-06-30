"""
Base class for settings tabs
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QSettings


class BaseSettingsTab(QWidget):
    """Base class for settings tabs."""
    
    def __init__(self, parent=None):
        """Initialize the base settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.main_layout = QVBoxLayout(self)
        self.settings = QSettings("POEditor", "Settings")
        
    def load_settings(self):
        """Load settings from storage.
        
        This method should be overridden in derived classes.
        """
        pass
        
    def save_settings(self):
        """Save settings to storage.
        
        This method should be overridden in derived classes.
        """
        pass
