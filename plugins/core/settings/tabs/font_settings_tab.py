"""
Font settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QComboBox, QSpinBox, QCheckBox, 
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QPushButton, QFontDialog, QFontComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from plugins.core.settings.tabs import BaseSettingsTab
from core.lg import debug


class FontSettingsTab(BaseSettingsTab):
    """Font settings tab implementation."""
    
    def __init__(self, parent=None):
        """Initialize the font settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.editor_font_group = QGroupBox("Editor Font")
        self.editor_font_combo = QFontComboBox()
        self.editor_font_size_spin = QSpinBox()
        self.editor_font_preview = QLabel("AaBbCcDdEe 123456")
        self.editor_font_dialog_button = QPushButton("Choose Font...")
        
        self.interface_font_group = QGroupBox("Interface Font")
        self.interface_font_combo = QFontComboBox()
        self.interface_font_size_spin = QSpinBox()
        self.interface_font_preview = QLabel("AaBbCcDdEe 123456")
        self.interface_font_dialog_button = QPushButton("Choose Font...")
        
        self.font_options_group = QGroupBox("Font Options")
        self.use_antialiasing_check = QCheckBox("Use font antialiasing")
        
        self._setup_ui()
        self.load_settings()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Editor font section
        self.editor_font_group = QGroupBox("Editor Font")
        editor_font_layout = QVBoxLayout()
        
        editor_font_selector_layout = QHBoxLayout()
        editor_font_selector_layout.addWidget(QLabel("Font:"))
        
        self.editor_font_combo = QFontComboBox()
        self.editor_font_combo.currentFontChanged.connect(self._update_editor_font_preview)
        
        editor_font_selector_layout.addWidget(self.editor_font_combo, 1)
        
        editor_font_size_layout = QHBoxLayout()
        editor_font_size_layout.addWidget(QLabel("Size:"))
        
        self.editor_font_size_spin = QSpinBox()
        self.editor_font_size_spin.setRange(6, 72)
        self.editor_font_size_spin.setValue(10)
        self.editor_font_size_spin.valueChanged.connect(self._update_editor_font_preview)
        
        editor_font_size_layout.addWidget(self.editor_font_size_spin)
        editor_font_size_layout.addStretch()
        
        self.editor_font_preview = QLabel("AaBbCcDdEe 123456")
        self.editor_font_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor_font_preview.setStyleSheet(
            "padding: 10px; border: 1px solid #ccc; background-color: #f5f5f5;"
        )
        
        self.editor_font_dialog_button = QPushButton("Choose Font...")
        self.editor_font_dialog_button.clicked.connect(self._show_editor_font_dialog)
        
        editor_font_layout.addLayout(editor_font_selector_layout)
        editor_font_layout.addLayout(editor_font_size_layout)
        editor_font_layout.addWidget(self.editor_font_preview)
        editor_font_layout.addWidget(self.editor_font_dialog_button)
        
        self.editor_font_group.setLayout(editor_font_layout)
        self.main_layout.addWidget(self.editor_font_group)
        
        # Interface font section
        self.interface_font_group = QGroupBox("Interface Font")
        interface_font_layout = QVBoxLayout()
        
        interface_font_selector_layout = QHBoxLayout()
        interface_font_selector_layout.addWidget(QLabel("Font:"))
        
        self.interface_font_combo = QFontComboBox()
        self.interface_font_combo.currentFontChanged.connect(self._update_interface_font_preview)
        
        interface_font_selector_layout.addWidget(self.interface_font_combo, 1)
        
        interface_font_size_layout = QHBoxLayout()
        interface_font_size_layout.addWidget(QLabel("Size:"))
        
        self.interface_font_size_spin = QSpinBox()
        self.interface_font_size_spin.setRange(6, 72)
        self.interface_font_size_spin.setValue(9)
        self.interface_font_size_spin.valueChanged.connect(self._update_interface_font_preview)
        
        interface_font_size_layout.addWidget(self.interface_font_size_spin)
        interface_font_size_layout.addStretch()
        
        self.interface_font_preview = QLabel("AaBbCcDdEe 123456")
        self.interface_font_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.interface_font_preview.setStyleSheet(
            "padding: 10px; border: 1px solid #ccc; background-color: #f5f5f5;"
        )
        
        self.interface_font_dialog_button = QPushButton("Choose Font...")
        self.interface_font_dialog_button.clicked.connect(self._show_interface_font_dialog)
        
        interface_font_layout.addLayout(interface_font_selector_layout)
        interface_font_layout.addLayout(interface_font_size_layout)
        interface_font_layout.addWidget(self.interface_font_preview)
        interface_font_layout.addWidget(self.interface_font_dialog_button)
        
        self.interface_font_group.setLayout(interface_font_layout)
        self.main_layout.addWidget(self.interface_font_group)
        
        # Additional font options
        self.font_options_group = QGroupBox("Font Options")
        font_options_layout = QVBoxLayout()
        
        self.use_antialiasing_check = QCheckBox("Use font antialiasing")
        font_options_layout.addWidget(self.use_antialiasing_check)
        
        self.font_options_group.setLayout(font_options_layout)
        self.main_layout.addWidget(self.font_options_group)
        
        # Add spacer
        self.main_layout.addStretch()
        
        # Load settings
        self.load_settings()
    
    def _update_editor_font_preview(self):
        """Update the editor font preview."""
        font = self.editor_font_combo.currentFont()
        font.setPointSize(self.editor_font_size_spin.value())
        self.editor_font_preview.setFont(font)
    
    def _update_interface_font_preview(self):
        """Update the interface font preview."""
        font = self.interface_font_combo.currentFont()
        font.setPointSize(self.interface_font_size_spin.value())
        self.interface_font_preview.setFont(font)
    
    def _show_editor_font_dialog(self):
        """Show the editor font dialog."""
        if not self.editor_font_preview:
            return
            
        current_font = self.editor_font_preview.font()
        result = QFontDialog.getFont(current_font, self, "Select Editor Font")
        if len(result) == 2:
            font, ok = result
            if ok and isinstance(font, QFont):
                if self.editor_font_combo:
                    self.editor_font_combo.setCurrentFont(font)
                if self.editor_font_size_spin:
                    self.editor_font_size_spin.setValue(font.pointSize())
                if self.editor_font_preview:
                    self.editor_font_preview.setFont(font)
    
    def _show_interface_font_dialog(self):
        """Show the interface font dialog."""
        if not self.interface_font_preview:
            return
            
        current_font = self.interface_font_preview.font()
        result = QFontDialog.getFont(current_font, self, "Select Interface Font")
        if len(result) == 2:
            font, ok = result
            if ok and isinstance(font, QFont):
                if self.interface_font_combo:
                    self.interface_font_combo.setCurrentFont(font)
                if self.interface_font_size_spin:
                    self.interface_font_size_spin.setValue(font.pointSize())
                if self.interface_font_preview:
                    self.interface_font_preview.setFont(font)
    
    def load_settings(self):
        """Load font settings from storage."""
        try:
            # Editor font
            editor_font_family = self.settings.value("fonts/editor/family", "Courier New")
            editor_font_size_raw = self.settings.value("fonts/editor/size", 10)
            
            if not isinstance(editor_font_family, str):
                editor_font_family = "Courier New"
            
            # Convert font size to int safely
            try:
                if isinstance(editor_font_size_raw, str):
                    editor_font_size = int(editor_font_size_raw)
                elif isinstance(editor_font_size_raw, int):
                    editor_font_size = editor_font_size_raw
                elif isinstance(editor_font_size_raw, float):
                    editor_font_size = int(editor_font_size_raw)
                else:
                    editor_font_size = 10  # Default
            except (TypeError, ValueError):
                editor_font_size = 10  # Default
            
            editor_font = QFont()
            editor_font.setFamily(editor_font_family)
            editor_font.setPointSize(editor_font_size)
            
            if self.editor_font_combo:
                self.editor_font_combo.setCurrentFont(editor_font)
            if self.editor_font_size_spin:
                self.editor_font_size_spin.setValue(editor_font_size)
            if self.editor_font_preview:
                self.editor_font_preview.setFont(editor_font)
            
            # Interface font
            interface_font_family = self.settings.value("fonts/interface/family", "Arial")  # Default system font
            interface_font_size_raw = self.settings.value("fonts/interface/size", 9)
            
            if not isinstance(interface_font_family, str):
                interface_font_family = "Arial"
            
            # Convert interface font size to int safely
            try:
                if isinstance(interface_font_size_raw, str):
                    interface_font_size = int(interface_font_size_raw)
                elif isinstance(interface_font_size_raw, int):
                    interface_font_size = interface_font_size_raw
                elif isinstance(interface_font_size_raw, float):
                    interface_font_size = int(interface_font_size_raw)
                else:
                    interface_font_size = 9  # Default
            except (TypeError, ValueError):
                interface_font_size = 9  # Default
            
            interface_font = QFont()
            interface_font.setFamily(interface_font_family)
            interface_font.setPointSize(interface_font_size)
            
            if self.interface_font_combo:
                self.interface_font_combo.setCurrentFont(interface_font)
            if self.interface_font_size_spin:
                self.interface_font_size_spin.setValue(interface_font_size)
            if self.interface_font_preview:
                self.interface_font_preview.setFont(interface_font)
            
            # Font options
            if self.use_antialiasing_check:
                use_antialiasing_raw = self.settings.value("fonts/use_antialiasing", True)
                if isinstance(use_antialiasing_raw, str):
                    use_antialiasing = use_antialiasing_raw.lower() == "true"
                else:
                    use_antialiasing = bool(use_antialiasing_raw)
                self.use_antialiasing_check.setChecked(use_antialiasing)
            
            debug("Font settings loaded")
        except Exception as e:
            debug(f"Error loading font settings: {str(e)}")
    
    def save_settings(self):
        """Save font settings to storage."""
        # Editor font
        editor_font = self.editor_font_combo.currentFont()
        editor_font_size = self.editor_font_size_spin.value()
        
        self.settings.setValue("fonts/editor/family", editor_font.family())
        self.settings.setValue("fonts/editor/size", editor_font_size)
        
        # Interface font
        interface_font = self.interface_font_combo.currentFont()
        interface_font_size = self.interface_font_size_spin.value()
        
        self.settings.setValue("fonts/interface/family", interface_font.family())
        self.settings.setValue("fonts/interface/size", interface_font_size)
        
        # Font options
        use_antialiasing = self.use_antialiasing_check.isChecked()
        self.settings.setValue("fonts/use_antialiasing", use_antialiasing)
        
        debug("Font settings saved")
