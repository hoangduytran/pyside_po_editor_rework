"""
Editor settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QCheckBox, QSpinBox, QComboBox,
    QGroupBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt

from plugins.core.settings.tabs import BaseSettingsTab


class EditorSettingsTab(BaseSettingsTab):
    """Editor settings tab."""
    
    def __init__(self, parent=None):
        """Initialize the editor settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.general_group = None
        self.display_line_numbers_check = None
        self.highlight_current_line_check = None
        self.word_wrap_check = None
        self.tab_size_spin = None
        self.use_spaces_check = None
        self.show_whitespace_check = None
        self.auto_indent_check = None
        
        self.syntax_group = None
        self.syntax_highlighting_check = None
        self.highlight_matching_brackets_check = None
        self.color_scheme_combo = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # General editor settings
        self.general_group = QGroupBox("General")
        general_layout = QVBoxLayout()
        
        self.display_line_numbers_check = QCheckBox("Display line numbers")
        self.highlight_current_line_check = QCheckBox("Highlight current line")
        self.word_wrap_check = QCheckBox("Word wrap")
        
        # Tab size
        tab_layout = QHBoxLayout()
        tab_layout.addWidget(QLabel("Tab size:"))
        
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 8)
        self.tab_size_spin.setValue(4)
        
        tab_layout.addWidget(self.tab_size_spin)
        tab_layout.addStretch()
        
        # Space settings
        self.use_spaces_check = QCheckBox("Use spaces instead of tabs")
        self.show_whitespace_check = QCheckBox("Show whitespace characters")
        self.auto_indent_check = QCheckBox("Auto-indent")
        
        general_layout.addWidget(self.display_line_numbers_check)
        general_layout.addWidget(self.highlight_current_line_check)
        general_layout.addWidget(self.word_wrap_check)
        general_layout.addLayout(tab_layout)
        general_layout.addWidget(self.use_spaces_check)
        general_layout.addWidget(self.show_whitespace_check)
        general_layout.addWidget(self.auto_indent_check)
        
        self.general_group.setLayout(general_layout)
        self.main_layout.addWidget(self.general_group)
        
        # Syntax highlighting settings
        self.syntax_group = QGroupBox("Syntax Highlighting")
        syntax_layout = QVBoxLayout()
        
        self.syntax_highlighting_check = QCheckBox("Enable syntax highlighting")
        self.highlight_matching_brackets_check = QCheckBox("Highlight matching brackets")
        
        # Color scheme
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color scheme:"))
        
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(["Default", "Dark", "Light", "Solarized"])
        
        color_layout.addWidget(self.color_scheme_combo)
        color_layout.addStretch()
        
        syntax_layout.addWidget(self.syntax_highlighting_check)
        syntax_layout.addWidget(self.highlight_matching_brackets_check)
        syntax_layout.addLayout(color_layout)
        
        self.syntax_group.setLayout(syntax_layout)
        self.main_layout.addWidget(self.syntax_group)
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch()
        
    def load_settings(self):
        """Load settings from storage."""
        # General editor settings
        if self.display_line_numbers_check:
            display_lines = self.settings.value("editor/display_line_numbers", True)
            if isinstance(display_lines, str):
                display_lines = display_lines.lower() == "true"
            self.display_line_numbers_check.setChecked(bool(display_lines))
            
        if self.highlight_current_line_check:
            highlight_line = self.settings.value("editor/highlight_current_line", True)
            if isinstance(highlight_line, str):
                highlight_line = highlight_line.lower() == "true"
            self.highlight_current_line_check.setChecked(bool(highlight_line))
            
        if self.word_wrap_check:
            word_wrap = self.settings.value("editor/word_wrap", False)
            if isinstance(word_wrap, str):
                word_wrap = word_wrap.lower() == "true"
            self.word_wrap_check.setChecked(bool(word_wrap))
            
        if self.tab_size_spin:
            tab_size = self.settings.value("editor/tab_size", 4)
            try:
                # Handle different types that might be returned
                if isinstance(tab_size, str):
                    tab_size_int = int(tab_size)
                elif isinstance(tab_size, int):
                    tab_size_int = tab_size
                elif isinstance(tab_size, float):
                    tab_size_int = int(tab_size)
                else:
                    # Default value
                    tab_size_int = 4
                self.tab_size_spin.setValue(tab_size_int)
            except (TypeError, ValueError):
                self.tab_size_spin.setValue(4)  # Default if conversion fails
                
        if self.use_spaces_check:
            use_spaces = self.settings.value("editor/use_spaces", True)
            if isinstance(use_spaces, str):
                use_spaces = use_spaces.lower() == "true"
            self.use_spaces_check.setChecked(bool(use_spaces))
            
        if self.show_whitespace_check:
            show_whitespace = self.settings.value("editor/show_whitespace", False)
            if isinstance(show_whitespace, str):
                show_whitespace = show_whitespace.lower() == "true"
            self.show_whitespace_check.setChecked(bool(show_whitespace))
            
        if self.auto_indent_check:
            auto_indent = self.settings.value("editor/auto_indent", True)
            if isinstance(auto_indent, str):
                auto_indent = auto_indent.lower() == "true"
            self.auto_indent_check.setChecked(bool(auto_indent))
        
        # Syntax highlighting settings
        if self.syntax_highlighting_check:
            syntax_highlighting = self.settings.value("editor/syntax_highlighting", True)
            if isinstance(syntax_highlighting, str):
                syntax_highlighting = syntax_highlighting.lower() == "true"
            self.syntax_highlighting_check.setChecked(bool(syntax_highlighting))
            
        if self.highlight_matching_brackets_check:
            highlight_brackets = self.settings.value("editor/highlight_brackets", True)
            if isinstance(highlight_brackets, str):
                highlight_brackets = highlight_brackets.lower() == "true"
            self.highlight_matching_brackets_check.setChecked(bool(highlight_brackets))
        
        if self.color_scheme_combo:
            color_scheme = self.settings.value("editor/color_scheme", "Default")
            if color_scheme:
                color_scheme_str = str(color_scheme)
                index = self.color_scheme_combo.findText(color_scheme_str)
                if index >= 0:
                    self.color_scheme_combo.setCurrentIndex(index)
        
    def save_settings(self):
        """Save settings to storage."""
        # General editor settings
        if self.display_line_numbers_check:
            self.settings.setValue("editor/display_line_numbers", self.display_line_numbers_check.isChecked())
            
        if self.highlight_current_line_check:
            self.settings.setValue("editor/highlight_current_line", self.highlight_current_line_check.isChecked())
            
        if self.word_wrap_check:
            self.settings.setValue("editor/word_wrap", self.word_wrap_check.isChecked())
            
        if self.tab_size_spin:
            self.settings.setValue("editor/tab_size", self.tab_size_spin.value())
            
        if self.use_spaces_check:
            self.settings.setValue("editor/use_spaces", self.use_spaces_check.isChecked())
            
        if self.show_whitespace_check:
            self.settings.setValue("editor/show_whitespace", self.show_whitespace_check.isChecked())
            
        if self.auto_indent_check:
            self.settings.setValue("editor/auto_indent", self.auto_indent_check.isChecked())
        
        # Syntax highlighting settings
        if self.syntax_highlighting_check:
            self.settings.setValue("editor/syntax_highlighting", self.syntax_highlighting_check.isChecked())
            
        if self.highlight_matching_brackets_check:
            self.settings.setValue("editor/highlight_brackets", self.highlight_matching_brackets_check.isChecked())
            
        if self.color_scheme_combo:
            self.settings.setValue("editor/color_scheme", self.color_scheme_combo.currentText())
