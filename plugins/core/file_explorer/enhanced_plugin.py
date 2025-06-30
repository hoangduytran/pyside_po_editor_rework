"""
Enhanced File Explorer Plugin - Integrates with sidebar system.
"""

from PySide6.QtWidgets import (
    QTreeView, QVBoxLayout, QWidget, QFileSystemModel, QHeaderView,
    QHBoxLayout, QPushButton, QLineEdit, QLabel
)
from PySide6.QtCore import QDir, Signal, Qt

from core.plugin_manager import Plugin
from core.abstract_panel import AbstractPanel


class FileExplorerWidget(QWidget):
    """Enhanced file explorer widget with toolbar and tree view."""
    
    # Signals
    file_selected = Signal(str)  # File path selected
    directory_changed = Signal(str)  # Directory changed
    
    def __init__(self, parent=None):
        """Initialize the file explorer widget."""
        super().__init__(parent)
        
        # Initialize all attributes in __init__
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.path_edit = QLineEdit()
        self.refresh_button = QPushButton("⟲")
        self.up_button = QPushButton("↑")
        self.current_path = QDir.currentPath()
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the file explorer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)
        
        # Up button
        self.up_button.setFixedSize(24, 24)
        self.up_button.setToolTip("Go up one directory")
        toolbar_layout.addWidget(self.up_button)
        
        # Path edit
        self.path_edit.setText(self.current_path)
        self.path_edit.setPlaceholderText("Enter path...")
        toolbar_layout.addWidget(self.path_edit)
        
        # Refresh button
        self.refresh_button.setFixedSize(24, 24)
        self.refresh_button.setToolTip("Refresh")
        toolbar_layout.addWidget(self.refresh_button)
        
        layout.addWidget(toolbar)
        
        # Tree view
        self.file_model.setRootPath(self.current_path)
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(self.current_path))
        
        # Configure tree view
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.tree_view.setSortingEnabled(True)
        
        # Hide unnecessary columns (keep name and size)
        header = self.tree_view.header()
        header.hideSection(1)  # Size - we'll keep this
        header.hideSection(2)  # Type
        header.hideSection(3)  # Date Modified
        
        layout.addWidget(self.tree_view)
        
    def _connect_signals(self):
        """Connect widget signals."""
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.path_edit.returnPressed.connect(self._on_path_changed)
        self.refresh_button.clicked.connect(self._refresh)
        self.up_button.clicked.connect(self._go_up)
        
    def _on_item_clicked(self, index):
        """Handle item click.
        
        Args:
            index: Model index of clicked item
        """
        file_path = self.file_model.filePath(index)
        self.file_selected.emit(file_path)
        
    def _on_item_double_clicked(self, index):
        """Handle item double click.
        
        Args:
            index: Model index of double-clicked item
        """
        file_path = self.file_model.filePath(index)
        
        if self.file_model.isDir(index):
            self.set_root_path(file_path)
        else:
            # TODO: Open file in editor
            print(f"Open file: {file_path}")
            
    def _on_path_changed(self):
        """Handle path edit change."""
        new_path = self.path_edit.text()
        if QDir(new_path).exists():
            self.set_root_path(new_path)
        else:
            # Reset to current path if invalid
            self.path_edit.setText(self.current_path)
            
    def _refresh(self):
        """Refresh the current directory."""
        self.file_model.setRootPath("")  # Clear cache
        self.file_model.setRootPath(self.current_path)
        
    def _go_up(self):
        """Go up one directory level."""
        parent_dir = QDir(self.current_path)
        if parent_dir.cdUp():
            self.set_root_path(parent_dir.absolutePath())
            
    def set_root_path(self, path: str):
        """Set the root path for the file explorer.
        
        Args:
            path: Root directory path
        """
        if QDir(path).exists():
            self.current_path = path
            self.file_model.setRootPath(path)
            self.tree_view.setRootIndex(self.file_model.index(path))
            self.path_edit.setText(path)
            self.directory_changed.emit(path)


class FileExplorerPanel(AbstractPanel):
    """File explorer panel for browsing files and directories."""
    
    def __init__(self, parent=None):
        """Initialize the file explorer panel."""
        super().__init__("File Explorer", parent)
        
        # Initialize all attributes in __init__
        self.explorer_widget = FileExplorerWidget()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the file explorer panel UI."""
        self.setWidget(self.explorer_widget)
        
    def set_root_path(self, path: str):
        """Set the root path for the file explorer.
        
        Args:
            path: Root directory path
        """
        self.explorer_widget.set_root_path(path)


class EnhancedFileExplorerPlugin(Plugin):
    """Enhanced File Explorer plugin implementation."""
    
    def __init__(self, name: str):
        """Initialize the plugin."""
        super().__init__(name, "2.0.0")
        
        # Initialize all attributes in __init__
        self.file_explorer_panel = None
        
    def load(self) -> bool:
        """Load the file explorer plugin."""
        try:
            self.file_explorer_panel = FileExplorerPanel()
            print("Enhanced File Explorer plugin loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load Enhanced File Explorer plugin: {e}")
            return False
            
    def unload(self) -> bool:
        """Unload the file explorer plugin."""
        try:
            if self.file_explorer_panel:
                self.file_explorer_panel.close()
                self.file_explorer_panel = None
            print("Enhanced File Explorer plugin unloaded successfully")
            return True
        except Exception as e:
            print(f"Failed to unload Enhanced File Explorer plugin: {e}")
            return False
            
    def get_panels(self):
        """Get panels provided by this plugin."""
        return [self.file_explorer_panel] if self.file_explorer_panel else []
