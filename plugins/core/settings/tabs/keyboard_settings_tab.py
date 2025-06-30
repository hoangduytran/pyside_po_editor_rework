"""
Keyboard settings tab implementation.
"""

from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QHBoxLayout, QVBoxLayout,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QKeySequence

from plugins.core.settings.tabs import BaseSettingsTab


class KeySequenceDialog(QDialog):
    """Dialog for capturing key sequences."""
    
    def __init__(self, action_name, current_sequence="", parent=None):
        """Initialize the key sequence dialog.
        
        Args:
            action_name: Name of the action
            current_sequence: Current key sequence
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.action_name = action_name
        self.current_sequence = current_sequence
        self.key_sequence = None
        self.main_layout = QVBoxLayout(self)
        self.form_layout = None
        self.key_edit = None
        self.button_box = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Configure Key Sequence")
        self.resize(400, 150)
        
        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel(f"Action: {self.action_name}"))
        
        # Key sequence edit
        self.key_edit = QLineEdit()
        self.key_edit.setText(self.current_sequence)
        self.key_edit.setPlaceholderText("Type new key sequence")
        self.key_edit.setReadOnly(True)
        
        # Install event filter to catch key presses
        self.key_edit.installEventFilter(self)
        
        self.form_layout.addRow("Key Sequence:", self.key_edit)
        
        # Clear button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear_sequence)
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.addButton(clear_button, QDialogButtonBox.ButtonRole.ActionRole)
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.button_box)
        
    def eventFilter(self, obj, event):
        """Filter key press events.
        
        Args:
            obj: Object being filtered
            event: Event to filter
            
        Returns:
            True if event was handled, otherwise default handling
        """
        if obj == self.key_edit and event.type() == event.Type.KeyPress:
            # Get the key sequence
            sequence = QKeySequence(event.keyCombination())
            if not sequence.isEmpty():
                self.key_sequence = sequence
                if self.key_edit:
                    self.key_edit.setText(sequence.toString())
                return True
                
        return super().eventFilter(obj, event)
        
    def _clear_sequence(self):
        """Clear the key sequence."""
        self.key_sequence = QKeySequence()
        if self.key_edit:
            self.key_edit.clear()
        
    def get_key_sequence(self):
        """Get the captured key sequence.
        
        Returns:
            QKeySequence object
        """
        return self.key_sequence or QKeySequence(self.current_sequence)


class KeyboardSettingsTab(BaseSettingsTab):
    """Keyboard settings tab."""
    
    def __init__(self, parent=None):
        """Initialize the keyboard settings tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.preset_combo = None
        self.shortcuts_table = None
        self.edit_button = None
        self.reset_button = None
        
        # Dictionary of keyboard shortcuts
        self.shortcuts = {}
        
        # Available presets
        self.presets = {
            "Default": {
                "Open File": "Ctrl+O",
                "Save": "Ctrl+S",
                "Save As": "Ctrl+Shift+S",
                "Find": "Ctrl+F",
                "Replace": "Ctrl+H",
                "Go to Next Entry": "Ctrl+Down",
                "Go to Previous Entry": "Ctrl+Up",
                "Mark as Translated": "Ctrl+T",
                "Copy Source to Target": "Ctrl+Space",
                "Show Context": "F2",
                "Show Translation Memory": "F3",
                "Show Machine Translation": "F4"
            },
            "Emacs": {
                "Open File": "Ctrl+X Ctrl+F",
                "Save": "Ctrl+X Ctrl+S",
                "Save As": "Ctrl+X Ctrl+W",
                "Find": "Ctrl+S",
                "Replace": "Alt+%",
                "Go to Next Entry": "Alt+N",
                "Go to Previous Entry": "Alt+P",
                "Mark as Translated": "Ctrl+C Ctrl+T",
                "Copy Source to Target": "Ctrl+C Ctrl+Y",
                "Show Context": "Ctrl+C 1",
                "Show Translation Memory": "Ctrl+C 2",
                "Show Machine Translation": "Ctrl+C 3"
            }
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Preset selection
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Keyboard preset:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(self.presets.keys()) + ["Custom"])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        
        self.main_layout.addLayout(preset_layout)
        
        # Shortcuts table
        self.shortcuts_table = QTableWidget(0, 2)
        self.shortcuts_table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.shortcuts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.shortcuts_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.shortcuts_table.setMinimumHeight(300)
        
        self.main_layout.addWidget(self.shortcuts_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Shortcut")
        self.edit_button.clicked.connect(self._edit_shortcut)
        
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._reset_shortcuts)
        
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        
        self.main_layout.addLayout(buttons_layout)
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch()
        
    def _on_preset_changed(self, preset_name):
        """Handle preset selection change.
        
        Args:
            preset_name: Name of the selected preset
        """
        if preset_name in self.presets:
            self.shortcuts = self.presets[preset_name].copy()
            self._update_shortcuts_table()
        
    def _update_shortcuts_table(self):
        """Update the shortcuts table with current shortcuts."""
        if not self.shortcuts_table:
            return
            
        self.shortcuts_table.setRowCount(0)
        
        for i, (action, shortcut) in enumerate(self.shortcuts.items()):
            self.shortcuts_table.insertRow(i)
            self.shortcuts_table.setItem(i, 0, QTableWidgetItem(action))
            self.shortcuts_table.setItem(i, 1, QTableWidgetItem(shortcut))
            
    def _edit_shortcut(self):
        """Edit the selected shortcut."""
        if not self.shortcuts_table:
            return
            
        current_row = self.shortcuts_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a shortcut to edit.")
            return
        
        # Check if items exist
        action_item = self.shortcuts_table.item(current_row, 0)
        shortcut_item = self.shortcuts_table.item(current_row, 1)
        
        if not action_item or not shortcut_item:
            return
            
        action = action_item.text()
        current_shortcut = shortcut_item.text()
        
        dialog = KeySequenceDialog(action, current_shortcut, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_sequence = dialog.get_key_sequence().toString()
            self.shortcuts[action] = new_sequence
            
            shortcut_item = self.shortcuts_table.item(current_row, 1)
            if shortcut_item:
                shortcut_item.setText(new_sequence)
            
            # If shortcuts were modified, switch to "Custom" preset
            if self.preset_combo:
                custom_index = self.preset_combo.findText("Custom")
                if custom_index >= 0:
                    self.preset_combo.setCurrentIndex(custom_index)
        
    def _reset_shortcuts(self):
        """Reset shortcuts to default."""
        if self.preset_combo:
            default_index = self.preset_combo.findText("Default")
            if default_index >= 0:
                self.preset_combo.setCurrentIndex(default_index)
        
    def load_settings(self):
        """Load settings from storage."""
        # Load shortcut settings
        if self.settings.contains("keyboard/shortcuts"):
            # Try to load shortcuts from settings
            try:
                shortcuts_dict = self.settings.value("keyboard/shortcuts")
                if isinstance(shortcuts_dict, dict):
                    self.shortcuts = shortcuts_dict
                else:
                    # Fall back to default shortcuts
                    self.shortcuts = self.presets["Default"].copy()
            except:
                # Fall back to default shortcuts
                self.shortcuts = self.presets["Default"].copy()
        else:
            # Use default shortcuts if not found in settings
            self.shortcuts = self.presets["Default"].copy()
            
        # Determine which preset is active if we have a preset combo
        if self.preset_combo:
            preset_found = False
            for preset_name, preset_shortcuts in self.presets.items():
                if self.shortcuts == preset_shortcuts:
                    preset_index = self.preset_combo.findText(preset_name)
                    if preset_index >= 0:
                        self.preset_combo.setCurrentIndex(preset_index)
                        preset_found = True
                        break
                    
            if not preset_found:
                # If no matching preset found, select "Custom"
                custom_index = self.preset_combo.findText("Custom")
                if custom_index >= 0:
                    self.preset_combo.setCurrentIndex(custom_index)
                
        # Update the table
        self._update_shortcuts_table()
        
    def save_settings(self):
        """Save settings to storage."""
        # Save shortcut settings
        if self.shortcuts:
            self.settings.setValue("keyboard/shortcuts", self.shortcuts)
