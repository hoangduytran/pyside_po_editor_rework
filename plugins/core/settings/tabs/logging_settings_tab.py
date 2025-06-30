"""
Logging settings tab implementation.
"""

import os
import logging
from PySide6.QtWidgets import (
    QLabel, QComboBox, QSpinBox, QCheckBox, 
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt

from plugins.core.settings.tabs import BaseSettingsTab
from core.lg import debug


class LoggingSettingsTab(BaseSettingsTab):
    """Logging settings tab implementation."""
    
    def __init__(self, parent=None):
        """Initialize the logging settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables with actual objects
        self.log_dir_group = QGroupBox("Log Directory")
        self.log_dir_edit = QLineEdit()
        self.log_dir_button = QPushButton("Browse...")
        
        self.log_options_group = QGroupBox("Log Options")
        self.console_logging_check = QCheckBox("Enable console logging")
        self.file_logging_check = QCheckBox("Enable file logging")
        self.log_level_combo = QComboBox()
        
        self.log_rotation_group = QGroupBox("Log Rotation")
        self.max_file_size_spin = QSpinBox()
        self.backup_count_spin = QSpinBox()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Log directory section
        self.log_dir_group = QGroupBox("Log Directory")
        log_dir_layout = QHBoxLayout()
        
        self.log_dir_edit = QLineEdit()
        self.log_dir_edit.setPlaceholderText("Path to log directory")
        
        self.log_dir_button = QPushButton("Browse...")
        self.log_dir_button.clicked.connect(self._browse_log_dir)
        
        log_dir_layout.addWidget(self.log_dir_edit, 1)
        log_dir_layout.addWidget(self.log_dir_button)
        
        self.log_dir_group.setLayout(log_dir_layout)
        self.main_layout.addWidget(self.log_dir_group)
        
        # Log options section
        self.log_options_group = QGroupBox("Log Options")
        log_options_layout = QVBoxLayout()
        
        self.console_logging_check = QCheckBox("Enable console logging")
        self.file_logging_check = QCheckBox("Enable file logging")
        
        # Log level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Log level:"))
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
        level_layout.addWidget(self.log_level_combo, 1)
        
        log_options_layout.addWidget(self.console_logging_check)
        log_options_layout.addWidget(self.file_logging_check)
        log_options_layout.addLayout(level_layout)
        
        self.log_options_group.setLayout(log_options_layout)
        self.main_layout.addWidget(self.log_options_group)
        
        # Log rotation section
        self.log_rotation_group = QGroupBox("Log Rotation")
        log_rotation_layout = QVBoxLayout()
        
        # Max file size
        file_size_layout = QHBoxLayout()
        file_size_layout.addWidget(QLabel("Maximum log file size (KB):"))
        
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(50, 10240)  # 50KB to 10MB
        self.max_file_size_spin.setValue(1024)  # 1MB default
        self.max_file_size_spin.setSingleStep(50)
        
        file_size_layout.addWidget(self.max_file_size_spin, 1)
        
        # Backup count
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Number of backup files:"))
        
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 20)
        self.backup_count_spin.setValue(5)
        
        backup_layout.addWidget(self.backup_count_spin, 1)
        
        log_rotation_layout.addLayout(file_size_layout)
        log_rotation_layout.addLayout(backup_layout)
        
        self.log_rotation_group.setLayout(log_rotation_layout)
        self.main_layout.addWidget(self.log_rotation_group)
        
        # Add spacer
        self.main_layout.addStretch()
        
        # Load settings
        self.load_settings()
    
    def _browse_log_dir(self):
        """Open file dialog to choose log directory."""
        current_dir = self.log_dir_edit.text()
        if not current_dir:
            current_dir = os.path.expanduser('~')
            
        directory = QFileDialog.getExistingDirectory(
            self, "Select Log Directory", current_dir
        )
        
        if directory:
            self.log_dir_edit.setText(directory)
    
    def load_settings(self):
        """Load logging settings from storage."""
        try:
            # Log directory
            default_log_dir = os.path.join(os.path.expanduser('~'), '.poeditor', 'logs')
            log_dir = self.settings.value("logging/log_dir", default_log_dir)
            
            if isinstance(log_dir, str):
                self.log_dir_edit.setText(log_dir)
            else:
                self.log_dir_edit.setText(default_log_dir)
            
            # Log options
            console_logging = self.settings.value("logging/console_logging", True, type=bool)
            file_logging = self.settings.value("logging/file_logging", True, type=bool)
            
            if isinstance(console_logging, bool):
                self.console_logging_check.setChecked(console_logging)
            else:
                self.console_logging_check.setChecked(True)
                
            if isinstance(file_logging, bool):
                self.file_logging_check.setChecked(file_logging)
            else:
                self.file_logging_check.setChecked(True)
            
            # Log level - populate combo box if needed
            if self.log_level_combo.count() == 0:
                self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
                
            log_level = self.settings.value("logging/log_level", "INFO")
            if isinstance(log_level, str):
                index = self.log_level_combo.findText(log_level)
                if index >= 0:
                    self.log_level_combo.setCurrentIndex(index)
            
            # Log rotation
            max_file_size = self.settings.value("logging/max_file_size", 1024 * 1024, type=int)
            if isinstance(max_file_size, int):
                max_file_size_kb = max_file_size // 1024  # Convert to KB
                self.max_file_size_spin.setValue(max_file_size_kb)
            else:
                self.max_file_size_spin.setValue(1024)  # Default 1MB
            
            backup_count = self.settings.value("logging/backup_count", 5, type=int)
            if isinstance(backup_count, int):
                self.backup_count_spin.setValue(backup_count)
            else:
                self.backup_count_spin.setValue(5)  # Default 5 backup files
            
            debug("Logging settings loaded")
        except Exception as e:
            debug(f"Error loading logging settings: {str(e)}")
    
    def save_settings(self):
        """Save logging settings to storage."""
        try:
            # Log directory
            log_dir = self.log_dir_edit.text()
            self.settings.setValue("logging/log_dir", log_dir)
            
            # Log options
            console_logging = self.console_logging_check.isChecked()
            file_logging = self.file_logging_check.isChecked()
            
            self.settings.setValue("logging/console_logging", console_logging)
            self.settings.setValue("logging/file_logging", file_logging)
            
            # Log level
            log_level = self.log_level_combo.currentText()
            self.settings.setValue("logging/log_level", log_level)
            
            # Log rotation
            max_file_size_kb = self.max_file_size_spin.value()
            max_file_size = max_file_size_kb * 1024  # Convert to bytes
            self.settings.setValue("logging/max_file_size", max_file_size)
            
            backup_count = self.backup_count_spin.value()
            self.settings.setValue("logging/backup_count", backup_count)
            
            debug("Logging settings saved")
        except Exception as e:
            debug(f"Error saving logging settings: {str(e)}")
