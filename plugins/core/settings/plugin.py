"""
Settings plugin for the PO Editor application.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt

from core.abstract_panel import AbstractPanel
from core.plugin_manager import Plugin
from core.lg import info, debug, error

from plugins.core.settings.preferences_dialog import PreferencesDialog


class SettingsPanel(AbstractPanel):
    """Panel for settings and preferences."""
    
    def __init__(self, parent=None):
        """Initialize the settings panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Settings", parent)
        
        # Initialize widget references
        self.main_layout = None
        self.preferences_button = None
        self.preferences_dialog = None
        self.title_label = None
        
        # Create a central widget for the dock widget
        self.central_widget = QWidget()
        self.setWidget(self.central_widget)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel("Settings")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.title_label)
        
        # Preferences button
        self.preferences_button = QPushButton("Open Preferences")
        self.preferences_button.clicked.connect(self._show_preferences)
        self.main_layout.addWidget(self.preferences_button)
        
        # Add spacer to push content to the top
        self.main_layout.addStretch()
        
    def _show_preferences(self):
        """Show the preferences dialog."""
        info("Opening preferences dialog")
        if not self.preferences_dialog:
            self.preferences_dialog = PreferencesDialog(self)
            
        # Show the dialog
        self.preferences_dialog.exec()
        
    def get_title(self) -> str:
        """Get the panel title.
        
        Returns:
            Panel title
        """
        return "Settings"


class SettingsPlugin(Plugin):
    """Plugin for settings and preferences."""
    
    def __init__(self, name=None):
        """Initialize the settings plugin."""
        super().__init__("settings" if name is None else name)
        
        # Initialize panel reference
        self.settings_panel = None
        
    def initialize(self, main_window=None, database_manager=None):
        """Initialize the plugin."""
        super().initialize(main_window, database_manager)
        debug("Initializing Settings plugin")
        self.settings_panel = SettingsPanel()
        
        # Register panel with main window
        if self.main_window:
            self.main_window.register_panel("settings", self.settings_panel)
            
            # Add a menu item for preferences
            if hasattr(self.main_window, 'view_menu'):
                preferences_action = self.main_window.view_menu.addAction("Preferences...")
                preferences_action.triggered.connect(self._show_preferences)
                
        return True
    
    def _show_preferences(self):
        """Show the preferences dialog."""
        if self.settings_panel:
            self.settings_panel._show_preferences()
        
    def get_name(self) -> str:
        """Get the plugin name.
        
        Returns:
            Plugin name
        """
        return "settings"
        
    def get_version(self) -> str:
        """Get the plugin version.
        
        Returns:
            Plugin version
        """
        return "1.0.0"
        
    def get_panel(self) -> Optional[AbstractPanel]:
        """Get the plugin panel.
        
        Returns:
            Plugin panel
        """
        return self.settings_panel
