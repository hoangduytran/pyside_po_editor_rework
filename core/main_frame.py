"""
Main Frame - The main window for PO Editor application.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QStatusBar, QDockWidget, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from .abstract_panel import AbstractPanel


class MainFrame(QMainWindow):
    """Main window for the PO Editor application."""
    
    # Signals
    file_opened = Signal(str)
    file_saved = Signal(str)
    
    def __init__(self, plugin_manager=None, database_manager=None):
        """Initialize the main frame.
        
        Args:
            plugin_manager: The plugin manager instance
            database_manager: The database manager instance
        """
        super().__init__()
        
        self.plugin_manager = plugin_manager
        self.database_manager = database_manager
        self.panels = {}  # Dictionary to store registered panels
        
        self._setup_ui()
        self._setup_menus()
        self._setup_status_bar()
        
    def _setup_ui(self):
        """Set up the main UI."""
        self.setWindowTitle("PO Editor")
        self.setMinimumSize(1200, 800)
        
        # Central widget - main editor area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Placeholder for main editor
        self.main_editor = QTextEdit()
        self.main_editor.setPlaceholderText("Open a PO file to start editing...")
        layout.addWidget(self.main_editor)
        
    def _setup_menus(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        self.view_menu = view_menu  # Store reference for plugins to add items
        
        # Plugins menu
        plugins_menu = menubar.addMenu("&Plugins")
        self.plugins_menu = plugins_menu  # Store reference for plugins to add items
        
    def _setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def register_panel(self, panel_id: str, panel: AbstractPanel):
        """Register a panel with the main frame.
        
        Args:
            panel_id: Unique identifier for the panel
            panel: The panel instance
        """
        if panel_id in self.panels:
            print(f"Warning: Panel '{panel_id}' is already registered")
            return
            
        self.panels[panel_id] = panel
        
        # Add the panel as a dock widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, panel)
        
        # Add toggle action to View menu
        toggle_action = panel.toggleViewAction()
        toggle_action.setText(f"Show {panel.windowTitle()}")
        self.view_menu.addAction(toggle_action)
        
    def unregister_panel(self, panel_id: str):
        """Unregister a panel from the main frame.
        
        Args:
            panel_id: Unique identifier for the panel
        """
        if panel_id not in self.panels:
            return
            
        panel = self.panels[panel_id]
        self.removeDockWidget(panel)
        del self.panels[panel_id]
        
    def get_panel(self, panel_id: str) -> Optional[AbstractPanel]:
        """Get a panel by its ID.
        
        Args:
            panel_id: Unique identifier for the panel
            
        Returns:
            The panel instance or None if not found
        """
        return self.panels.get(panel_id)
        
    def open_file(self):
        """Handle file open action."""
        # TODO: Implement file dialog and PO file loading
        self.status_bar.showMessage("File -> Open clicked")
        
    def save_file(self):
        """Handle file save action."""
        # TODO: Implement file saving
        self.status_bar.showMessage("File -> Save clicked")
        
    def show_message(self, message: str, timeout: int = 5000):
        """Show a message in the status bar.
        
        Args:
            message: The message to show
            timeout: How long to show the message (ms)
        """
        self.status_bar.showMessage(message, timeout)
