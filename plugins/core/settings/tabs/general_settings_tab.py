"""
General settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QCheckBox, QLineEdit, QPushButton, 
    QFileDialog, QGroupBox, QHBoxLayout, QVBoxLayout,
    QComboBox
)
from PySide6.QtCore import Qt

from plugins.core.settings.tabs import BaseSettingsTab


class GeneralSettingsTab(BaseSettingsTab):
    """General application settings tab."""
    
    def __init__(self, parent=None):
        """Initialize the general settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.startup_behavior_group = None
        self.start_maximized_check = None
        self.remember_window_size_check = None
        self.remember_window_position_check = None
        self.restore_last_session_check = None
        
        self.file_handling_group = None
        self.auto_save_check = None
        self.auto_save_interval_combo = None
        self.backup_files_check = None
        self.default_open_dir_edit = None
        self.default_open_dir_button = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Startup behavior section
        self.startup_behavior_group = QGroupBox("Startup Behavior")
        startup_layout = QVBoxLayout()
        
        self.start_maximized_check = QCheckBox("Start maximized")
        self.remember_window_size_check = QCheckBox("Remember window size")
        self.remember_window_position_check = QCheckBox("Remember window position")
        self.restore_last_session_check = QCheckBox("Restore last session")
        
        startup_layout.addWidget(self.start_maximized_check)
        startup_layout.addWidget(self.remember_window_size_check)
        startup_layout.addWidget(self.remember_window_position_check)
        startup_layout.addWidget(self.restore_last_session_check)
        
        self.startup_behavior_group.setLayout(startup_layout)
        self.main_layout.addWidget(self.startup_behavior_group)
        
        # File handling section
        self.file_handling_group = QGroupBox("File Handling")
        file_layout = QVBoxLayout()
        
        self.auto_save_check = QCheckBox("Auto-save files")
        
        # Auto-save interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Auto-save interval:"))
        
        self.auto_save_interval_combo = QComboBox()
        self.auto_save_interval_combo.addItems(["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"])
        
        interval_layout.addWidget(self.auto_save_interval_combo)
        interval_layout.addStretch()
        
        # Backup files
        self.backup_files_check = QCheckBox("Create backup files")
        
        # Default open directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Default directory:"))
        
        self.default_open_dir_edit = QLineEdit()
        self.default_open_dir_button = QPushButton("Browse...")
        self.default_open_dir_button.clicked.connect(self._browse_default_dir)
        
        dir_layout.addWidget(self.default_open_dir_edit, 1)
        dir_layout.addWidget(self.default_open_dir_button)
        
        file_layout.addWidget(self.auto_save_check)
        file_layout.addLayout(interval_layout)
        file_layout.addWidget(self.backup_files_check)
        file_layout.addLayout(dir_layout)
        
        self.file_handling_group.setLayout(file_layout)
        self.main_layout.addWidget(self.file_handling_group)
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch()
        
    def _browse_default_dir(self):
        """Browse for default directory."""
        if self.default_open_dir_edit:
            current_dir = self.default_open_dir_edit.text() or ""
            dir_path = QFileDialog.getExistingDirectory(
                self, "Select Default Directory", current_dir
            )
            
            if dir_path and self.default_open_dir_edit:
                self.default_open_dir_edit.setText(dir_path)
        
    def load_settings(self):
        """Load settings from storage."""
        # Startup behavior
        if self.start_maximized_check:
            start_maximized = self.settings.value("general/start_maximized", False)
            if isinstance(start_maximized, str):
                start_maximized = start_maximized.lower() == "true"
            self.start_maximized_check.setChecked(bool(start_maximized))
            
        if self.remember_window_size_check:
            remember_size = self.settings.value("general/remember_window_size", True)
            if isinstance(remember_size, str):
                remember_size = remember_size.lower() == "true"
            self.remember_window_size_check.setChecked(bool(remember_size))
            
        if self.remember_window_position_check:
            remember_pos = self.settings.value("general/remember_window_position", True)
            if isinstance(remember_pos, str):
                remember_pos = remember_pos.lower() == "true"
            self.remember_window_position_check.setChecked(bool(remember_pos))
            
        if self.restore_last_session_check:
            restore_session = self.settings.value("general/restore_last_session", True)
            if isinstance(restore_session, str):
                restore_session = restore_session.lower() == "true"
            self.restore_last_session_check.setChecked(bool(restore_session))
        
        # File handling
        if self.auto_save_check:
            auto_save = self.settings.value("general/auto_save", True)
            if isinstance(auto_save, str):
                auto_save = auto_save.lower() == "true"
            self.auto_save_check.setChecked(bool(auto_save))
        
        # Auto save interval
        if self.auto_save_interval_combo:
            interval = self.settings.value("general/auto_save_interval", "5 minutes")
            if interval:
                interval_str = str(interval)
                index = self.auto_save_interval_combo.findText(interval_str)
                if index >= 0:
                    self.auto_save_interval_combo.setCurrentIndex(index)
                    
        if self.backup_files_check:
            backup_files = self.settings.value("general/backup_files", True)
            if isinstance(backup_files, str):
                backup_files = backup_files.lower() == "true"
            self.backup_files_check.setChecked(bool(backup_files))
        
        # Default directory
        if self.default_open_dir_edit:
            dir_path = self.settings.value("general/default_open_dir", "")
            self.default_open_dir_edit.setText(str(dir_path) if dir_path else "")
        
    def save_settings(self):
        """Save settings to storage."""
        # Startup behavior
        if self.start_maximized_check:
            self.settings.setValue("general/start_maximized", self.start_maximized_check.isChecked())
        
        if self.remember_window_size_check:
            self.settings.setValue("general/remember_window_size", self.remember_window_size_check.isChecked())
        
        if self.remember_window_position_check:
            self.settings.setValue("general/remember_window_position", self.remember_window_position_check.isChecked())
        
        if self.restore_last_session_check:
            self.settings.setValue("general/restore_last_session", self.restore_last_session_check.isChecked())
        
        # File handling
        if self.auto_save_check:
            self.settings.setValue("general/auto_save", self.auto_save_check.isChecked())
        
        if self.auto_save_interval_combo:
            self.settings.setValue("general/auto_save_interval", self.auto_save_interval_combo.currentText())
        
        if self.backup_files_check:
            self.settings.setValue("general/backup_files", self.backup_files_check.isChecked())
        
        if self.default_open_dir_edit:
            self.settings.setValue("general/default_open_dir", self.default_open_dir_edit.text())
