"""
Appearance settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QComboBox, QCheckBox, QPushButton, QColorDialog,
    QGroupBox, QHBoxLayout, QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from plugins.core.settings.tabs import BaseSettingsTab


class ColorButton(QPushButton):
    """Button that shows and allows selection of a color."""
    
    def __init__(self, color=None, parent=None):
        """Initialize the color button.
        
        Args:
            color: Initial color
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.current_color = color or QColor(Qt.GlobalColor.white)
        
        self.setFixedSize(30, 30)
        self._update_style()
        
        # Connect signals
        self.clicked.connect(self._choose_color)
        
    def _update_style(self):
        """Update the button style based on current color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                border: 1px solid #888888;
            }}
            QPushButton:hover {{
                border: 1px solid #000000;
            }}
        """)
        
    def _choose_color(self):
        """Open color dialog to choose a color."""
        color = QColorDialog.getColor(self.current_color, self, "Select Color")
        if color.isValid():
            self.set_color(color)
            
    def get_color(self):
        """Get the current color.
        
        Returns:
            Current QColor
        """
        return self.current_color
        
    def set_color(self, color):
        """Set the current color.
        
        Args:
            color: QColor to set
        """
        self.current_color = color
        self._update_style()


class AppearanceSettingsTab(BaseSettingsTab):
    """Appearance settings tab."""
    
    def __init__(self, parent=None):
        """Initialize the appearance settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.theme_group = None
        self.theme_combo = None
        self.use_custom_theme_check = None
        self.custom_colors_group = None
        
        self.background_color_button = None
        self.text_color_button = None
        self.selection_color_button = None
        self.highlight_color_button = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Theme selection
        self.theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        # Theme combo
        theme_combo_layout = QHBoxLayout()
        theme_combo_layout.addWidget(QLabel("Application theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark", "Custom"])
        
        theme_combo_layout.addWidget(self.theme_combo)
        theme_combo_layout.addStretch()
        
        # Custom theme checkbox
        self.use_custom_theme_check = QCheckBox("Use custom theme colors")
        self.use_custom_theme_check.toggled.connect(self._toggle_custom_theme)
        
        theme_layout.addLayout(theme_combo_layout)
        theme_layout.addWidget(self.use_custom_theme_check)
        
        self.theme_group.setLayout(theme_layout)
        self.main_layout.addWidget(self.theme_group)
        
        # Custom colors
        self.custom_colors_group = QGroupBox("Custom Colors")
        colors_layout = QVBoxLayout()
        
        # Background color
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("Background color:"))
        self.background_color_button = ColorButton(QColor("#FFFFFF"))
        bg_layout.addWidget(self.background_color_button)
        bg_layout.addStretch()
        
        # Text color
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text color:"))
        self.text_color_button = ColorButton(QColor("#000000"))
        text_layout.addWidget(self.text_color_button)
        text_layout.addStretch()
        
        # Selection color
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Selection color:"))
        self.selection_color_button = ColorButton(QColor("#4A90D9"))
        selection_layout.addWidget(self.selection_color_button)
        selection_layout.addStretch()
        
        # Highlight color
        highlight_layout = QHBoxLayout()
        highlight_layout.addWidget(QLabel("Highlight color:"))
        self.highlight_color_button = ColorButton(QColor("#FFD700"))
        highlight_layout.addWidget(self.highlight_color_button)
        highlight_layout.addStretch()
        
        colors_layout.addLayout(bg_layout)
        colors_layout.addLayout(text_layout)
        colors_layout.addLayout(selection_layout)
        colors_layout.addLayout(highlight_layout)
        
        self.custom_colors_group.setLayout(colors_layout)
        self.main_layout.addWidget(self.custom_colors_group)
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch()
        
        # Initialize state based on current settings
        self._toggle_custom_theme(self.use_custom_theme_check.isChecked())
        
    def _toggle_custom_theme(self, enabled):
        """Toggle the custom theme settings.
        
        Args:
            enabled: Whether to enable custom theme settings
        """
        if self.custom_colors_group:
            self.custom_colors_group.setEnabled(enabled)
        
        # If enabled, set theme to Custom
        if enabled and self.theme_combo:
            index = self.theme_combo.findText("Custom")
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
        
    def load_settings(self):
        """Load settings from storage."""
        # Theme
        if self.theme_combo:
            theme = self.settings.value("appearance/theme", "System")
            if theme:
                theme_str = str(theme)
                index = self.theme_combo.findText(theme_str)
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
            
        # Custom theme
        if self.use_custom_theme_check:
            use_custom = self.settings.value("appearance/use_custom_theme", False)
            if isinstance(use_custom, str):
                use_custom = use_custom.lower() == "true"
            self.use_custom_theme_check.setChecked(bool(use_custom))
        
        # Color settings
        if self.background_color_button:
            bg_color = self.settings.value("appearance/background_color", "#FFFFFF")
            if bg_color:
                self.background_color_button.set_color(QColor(str(bg_color)))
        
        if self.text_color_button:
            text_color = self.settings.value("appearance/text_color", "#000000")
            if text_color:
                self.text_color_button.set_color(QColor(str(text_color)))
        
        if self.selection_color_button:
            selection_color = self.settings.value("appearance/selection_color", "#4A90D9")
            if selection_color:
                self.selection_color_button.set_color(QColor(str(selection_color)))
        
        if self.highlight_color_button:
            highlight_color = self.settings.value("appearance/highlight_color", "#FFD700")
            if highlight_color:
                self.highlight_color_button.set_color(QColor(str(highlight_color)))
        
    def save_settings(self):
        """Save settings to storage."""
        # Theme
        if self.theme_combo:
            self.settings.setValue("appearance/theme", self.theme_combo.currentText())
        
        if self.use_custom_theme_check:
            self.settings.setValue("appearance/use_custom_theme", self.use_custom_theme_check.isChecked())
        
        # Color settings
        if self.background_color_button:
            self.settings.setValue("appearance/background_color", self.background_color_button.get_color().name())
        
        if self.text_color_button:
            self.settings.setValue("appearance/text_color", self.text_color_button.get_color().name())
        
        if self.selection_color_button:
            self.settings.setValue("appearance/selection_color", self.selection_color_button.get_color().name())
        
        if self.highlight_color_button:
            self.settings.setValue("appearance/highlight_color", self.highlight_color_button.get_color().name())
