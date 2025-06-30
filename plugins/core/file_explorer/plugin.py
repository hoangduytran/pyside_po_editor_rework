"""
File Explorer Plugin - Core plugin for file browsing functionality.
"""

from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget, QFileSystemModel
from PySide6.QtCore import QDir

from core.plugin_manager import Plugin
from core.abstract_panel import AbstractPanel


class FileExplorerPanel(AbstractPanel):
    """File explorer panel for browsing files and directories."""
    
    def __init__(self, parent=None):
        """Initialize the file explorer panel."""
        super().__init__("File Explorer", parent)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the file explorer UI."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create tree view with file system model
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.currentPath()))
        
        # Hide size, type, and date columns - only show name
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2) 
        self.tree_view.hideColumn(3)
        
        layout.addWidget(self.tree_view)
        self.setWidget(widget)
        
    def set_root_path(self, path: str):
        """Set the root path for the file explorer.
        
        Args:
            path: Root directory path
        """
        self.file_model.setRootPath(path)
        self.tree_view.setRootIndex(self.file_model.index(path))


class FileExplorerPlugin(Plugin):
    """File Explorer plugin implementation."""
    
    def __init__(self, name: str):
        """Initialize the plugin."""
        super().__init__(name, "1.0.0")
        self.file_explorer_panel = None
        
    def load(self) -> bool:
        """Load the file explorer plugin."""
        try:
            self.file_explorer_panel = FileExplorerPanel()
            print(f"File Explorer plugin loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load File Explorer plugin: {e}")
            return False
            
    def unload(self) -> bool:
        """Unload the file explorer plugin."""
        try:
            if self.file_explorer_panel:
                self.file_explorer_panel.close()
                self.file_explorer_panel = None
            print(f"File Explorer plugin unloaded successfully")
            return True
        except Exception as e:
            print(f"Failed to unload File Explorer plugin: {e}")
            return False
            
    def get_panels(self):
        """Get panels provided by this plugin."""
        return [self.file_explorer_panel] if self.file_explorer_panel else []
