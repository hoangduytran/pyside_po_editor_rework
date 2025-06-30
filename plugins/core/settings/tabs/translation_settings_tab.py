"""
Translation settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QCheckBox, QComboBox, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout, QVBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt

from plugins.core.settings.tabs import BaseSettingsTab


class TranslationSettingsTab(BaseSettingsTab):
    """Translation settings tab."""
    
    def __init__(self, parent=None):
        """Initialize the translation settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.po_group = None
        self.preserve_comments_check = None
        self.save_header_check = None
        self.wrap_lines_check = None
        self.line_wrap_width_spin = None
        
        self.trans_group = None
        self.default_source_lang_combo = None
        self.default_target_lang_combo = None
        self.auto_translate_check = None
        self.use_placeholders_check = None
        self.enable_history_check = None
        self.max_history_entries_spin = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # PO file settings
        self.po_group = QGroupBox("PO File Settings")
        po_layout = QVBoxLayout()
        
        self.preserve_comments_check = QCheckBox("Preserve comments")
        self.save_header_check = QCheckBox("Save header information")
        self.wrap_lines_check = QCheckBox("Wrap long lines")
        
        # Line wrap width
        wrap_layout = QHBoxLayout()
        wrap_layout.addWidget(QLabel("Line wrap width:"))
        
        self.line_wrap_width_spin = QSpinBox()
        self.line_wrap_width_spin.setRange(40, 200)
        self.line_wrap_width_spin.setValue(79)
        
        wrap_layout.addWidget(self.line_wrap_width_spin)
        wrap_layout.addStretch()
        
        po_layout.addWidget(self.preserve_comments_check)
        po_layout.addWidget(self.save_header_check)
        po_layout.addWidget(self.wrap_lines_check)
        po_layout.addLayout(wrap_layout)
        
        self.po_group.setLayout(po_layout)
        self.main_layout.addWidget(self.po_group)
        
        # Translation settings
        self.trans_group = QGroupBox("Translation Settings")
        trans_layout = QVBoxLayout()
        
        # Default languages
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Default source language:"))
        
        self.default_source_lang_combo = QComboBox()
        self.default_source_lang_combo.addItems(["English", "French", "German", "Spanish", "Italian", "Chinese", "Japanese"])
        
        source_layout.addWidget(self.default_source_lang_combo)
        source_layout.addStretch()
        
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Default target language:"))
        
        self.default_target_lang_combo = QComboBox()
        self.default_target_lang_combo.addItems(["English", "French", "German", "Spanish", "Italian", "Chinese", "Japanese"])
        
        target_layout.addWidget(self.default_target_lang_combo)
        target_layout.addStretch()
        
        # Translation options
        self.auto_translate_check = QCheckBox("Auto-translate empty entries")
        self.use_placeholders_check = QCheckBox("Use placeholders for variables")
        self.enable_history_check = QCheckBox("Enable translation history")
        
        # History entries limit
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("Max history entries:"))
        
        self.max_history_entries_spin = QSpinBox()
        self.max_history_entries_spin.setRange(10, 1000)
        self.max_history_entries_spin.setValue(100)
        
        history_layout.addWidget(self.max_history_entries_spin)
        history_layout.addStretch()
        
        trans_layout.addLayout(source_layout)
        trans_layout.addLayout(target_layout)
        trans_layout.addWidget(self.auto_translate_check)
        trans_layout.addWidget(self.use_placeholders_check)
        trans_layout.addWidget(self.enable_history_check)
        trans_layout.addLayout(history_layout)
        
        self.trans_group.setLayout(trans_layout)
        self.main_layout.addWidget(self.trans_group)
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch()
        
    def load_settings(self):
        """Load settings from storage."""
        # PO file settings
        if self.preserve_comments_check:
            preserve_comments = self.settings.value("translation/preserve_comments", True)
            if isinstance(preserve_comments, str):
                preserve_comments = preserve_comments.lower() == "true"
            self.preserve_comments_check.setChecked(bool(preserve_comments))
            
        if self.save_header_check:
            save_header = self.settings.value("translation/save_header", True)
            if isinstance(save_header, str):
                save_header = save_header.lower() == "true"
            self.save_header_check.setChecked(bool(save_header))
            
        if self.wrap_lines_check:
            wrap_lines = self.settings.value("translation/wrap_lines", True)
            if isinstance(wrap_lines, str):
                wrap_lines = wrap_lines.lower() == "true"
            self.wrap_lines_check.setChecked(bool(wrap_lines))
            
        if self.line_wrap_width_spin:
            wrap_width = self.settings.value("translation/line_wrap_width", 79)
            try:
                if isinstance(wrap_width, str):
                    wrap_width_int = int(wrap_width)
                elif isinstance(wrap_width, int):
                    wrap_width_int = wrap_width
                elif isinstance(wrap_width, float):
                    wrap_width_int = int(wrap_width)
                else:
                    wrap_width_int = 79  # Default
                self.line_wrap_width_spin.setValue(wrap_width_int)
            except (TypeError, ValueError):
                self.line_wrap_width_spin.setValue(79)  # Default if conversion fails
        
        # Translation settings
        if self.default_source_lang_combo:
            source_lang = self.settings.value("translation/default_source_lang", "English")
            if source_lang:
                source_lang_str = str(source_lang)
                index = self.default_source_lang_combo.findText(source_lang_str)
                if index >= 0:
                    self.default_source_lang_combo.setCurrentIndex(index)
            
        if self.default_target_lang_combo:
            target_lang = self.settings.value("translation/default_target_lang", "French")
            if target_lang:
                target_lang_str = str(target_lang)
                index = self.default_target_lang_combo.findText(target_lang_str)
                if index >= 0:
                    self.default_target_lang_combo.setCurrentIndex(index)
            
        if self.auto_translate_check:
            auto_translate = self.settings.value("translation/auto_translate", False)
            if isinstance(auto_translate, str):
                auto_translate = auto_translate.lower() == "true"
            self.auto_translate_check.setChecked(bool(auto_translate))
            
        if self.use_placeholders_check:
            use_placeholders = self.settings.value("translation/use_placeholders", True)
            if isinstance(use_placeholders, str):
                use_placeholders = use_placeholders.lower() == "true"
            self.use_placeholders_check.setChecked(bool(use_placeholders))
            
        if self.enable_history_check:
            enable_history = self.settings.value("translation/enable_history", True)
            if isinstance(enable_history, str):
                enable_history = enable_history.lower() == "true"
            self.enable_history_check.setChecked(bool(enable_history))
            
        if self.max_history_entries_spin:
            max_entries = self.settings.value("translation/max_history_entries", 100)
            try:
                if isinstance(max_entries, str):
                    max_entries_int = int(max_entries)
                elif isinstance(max_entries, int):
                    max_entries_int = max_entries
                elif isinstance(max_entries, float):
                    max_entries_int = int(max_entries)
                else:
                    max_entries_int = 100  # Default
                self.max_history_entries_spin.setValue(max_entries_int)
            except (TypeError, ValueError):
                self.max_history_entries_spin.setValue(100)  # Default if conversion fails
        
    def save_settings(self):
        """Save settings to storage."""
        # PO file settings
        if self.preserve_comments_check:
            self.settings.setValue("translation/preserve_comments", self.preserve_comments_check.isChecked())
        
        if self.save_header_check:
            self.settings.setValue("translation/save_header", self.save_header_check.isChecked())
        
        if self.wrap_lines_check:
            self.settings.setValue("translation/wrap_lines", self.wrap_lines_check.isChecked())
        
        if self.line_wrap_width_spin:
            self.settings.setValue("translation/line_wrap_width", self.line_wrap_width_spin.value())
        
        # Translation settings
        if self.default_source_lang_combo:
            self.settings.setValue("translation/default_source_lang", self.default_source_lang_combo.currentText())
        
        if self.default_target_lang_combo:
            self.settings.setValue("translation/default_target_lang", self.default_target_lang_combo.currentText())
        
        if self.auto_translate_check:
            self.settings.setValue("translation/auto_translate", self.auto_translate_check.isChecked())
        
        if self.use_placeholders_check:
            self.settings.setValue("translation/use_placeholders", self.use_placeholders_check.isChecked())
        
        if self.enable_history_check:
            self.settings.setValue("translation/enable_history", self.enable_history_check.isChecked())
        
        if self.max_history_entries_spin:
            self.settings.setValue("translation/max_history_entries", self.max_history_entries_spin.value())
