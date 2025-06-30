"""
Preferences dialog implementation.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, 
    QDialogButtonBox
)
from PySide6.QtCore import Qt

from core.lg import debug, info

from plugins.core.settings.tabs.general_settings_tab import GeneralSettingsTab
from plugins.core.settings.tabs.editor_settings_tab import EditorSettingsTab
from plugins.core.settings.tabs.translation_settings_tab import TranslationSettingsTab
from plugins.core.settings.tabs.appearance_settings_tab import AppearanceSettingsTab
from plugins.core.settings.tabs.keyboard_settings_tab import KeyboardSettingsTab
from plugins.core.settings.tabs.font_settings_tab import FontSettingsTab
from plugins.core.settings.tabs.logging_settings_tab import LoggingSettingsTab


class PreferencesDialog(QDialog):
    """Preferences dialog with tabs for different setting categories."""
    
    def __init__(self, parent=None):
        """Initialize the preferences dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.tabs = {}
        self.tab_widget = QTabWidget(self)
        self.button_box = QDialogButtonBox()
        self.main_layout = QVBoxLayout(self)
        
        # Initialize tab references
        self.general_tab = None
        self.editor_tab = None
        self.translation_tab = None
        self.appearance_tab = None
        self.keyboard_tab = None
        self.font_tab = None
        self.logging_tab = None
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Preferences")
        self.resize(800, 600)
        
        # Main layout - already initialized in __init__
        
        # Tab widget - already initialized in __init__
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.general_tab = GeneralSettingsTab()
        self.editor_tab = EditorSettingsTab()
        self.translation_tab = TranslationSettingsTab()
        self.appearance_tab = AppearanceSettingsTab()
        self.keyboard_tab = KeyboardSettingsTab()
        self.font_tab = FontSettingsTab()
        self.logging_tab = LoggingSettingsTab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.editor_tab, "Editor")
        self.tab_widget.addTab(self.translation_tab, "Translation")
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.tab_widget.addTab(self.keyboard_tab, "Keyboard")
        self.tab_widget.addTab(self.font_tab, "Fonts")
        self.tab_widget.addTab(self.logging_tab, "Logging")
        
        # Store tabs in a dictionary for easier access
        self.tabs = {
            "general": self.general_tab,
            "editor": self.editor_tab,
            "translation": self.translation_tab,
            "appearance": self.appearance_tab,
            "keyboard": self.keyboard_tab,
            "font": self.font_tab,
            "logging": self.logging_tab
        }
        
        # Button box - already initialized in __init__
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._save_settings)
        
        self.main_layout.addWidget(self.button_box)
        
    def _load_settings(self):
        """Load settings for all tabs."""
        debug("Loading preferences dialog settings")
        
        # Load settings for each tab
        for tab_name, tab in self.tabs.items():
            try:
                tab.load_settings()
            except Exception as e:
                info(f"Failed to load settings for tab {tab_name}: {str(e)}")
        
    def _save_settings(self):
        """Save settings for all tabs."""
        debug("Saving preferences dialog settings")
        
        # Save settings for each tab
        for tab_name, tab in self.tabs.items():
            try:
                tab.save_settings()
            except Exception as e:
                info(f"Failed to save settings for tab {tab_name}: {str(e)}")
                
    def accept(self):
        """Handle dialog acceptance."""
        self._save_settings()
        super().accept()
        
    def get_active_tab(self) -> str:
        """Get the name of the currently active tab.
        
        Returns:
            Name of the active tab
        """
        current_index = self.tab_widget.currentIndex()
        for tab_name, tab in self.tabs.items():
            if self.tab_widget.indexOf(tab) == current_index:
                return tab_name
        return ""
        
    def set_active_tab(self, tab_name: str):
        """Set the active tab by name.
        
        Args:
            tab_name: Name of the tab to activate
        """
        if tab_name in self.tabs:
            tab = self.tabs[tab_name]
            index = self.tab_widget.indexOf(tab)
            if index >= 0:
                self.tab_widget.setCurrentIndex(index)
