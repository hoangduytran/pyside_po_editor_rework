"""
Sidebar Widget - Modern IDE-style sidebar with toggle buttons and panels
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPalette

from .abstract_panel import AbstractPanel


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation."""
    
    def __init__(self, text: str, icon_path: Optional[str] = None, parent=None):
        """Initialize sidebar button.
        
        Args:
            text: Button text
            icon_path: Optional path to icon
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize all attributes
        self.button_text = text
        self.icon_path = icon_path
        self.is_active = False
        self.panel_id = ""
        
        self._setup_button()
        
    def _setup_button(self):
        """Set up button appearance and properties."""
        self.setText(self.button_text)
        self.setCheckable(True)
        self.setFixedSize(QSize(40, 40))
        self.setToolTip(self.button_text)
        
        # Set style
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #cccccc;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
            }
        """)
        
    def set_active(self, active: bool):
        """Set button active state.
        
        Args:
            active: Whether button should be active
        """
        self.is_active = active
        self.setChecked(active)
        
    def set_panel_id(self, panel_id: str):
        """Set associated panel ID.
        
        Args:
            panel_id: ID of the panel this button controls
        """
        self.panel_id = panel_id


class SidebarWidget(QWidget):
    """Main sidebar widget with buttons and panels."""
    
    # Signals
    panel_requested = Signal(str)  # Panel ID
    panel_hidden = Signal(str)    # Panel ID
    
    def __init__(self, parent=None):
        """Initialize the sidebar widget."""
        super().__init__(parent)
        
        # Initialize all attributes first
        self.buttons: Dict[str, SidebarButton] = {}
        self.panels: Dict[str, AbstractPanel] = {}
        self.current_panel_id = ""
        self.is_sidebar_visible = True
        self.sidebar_width = 250
        
        # Initialize UI components to actual objects (not None)
        self.main_layout = QHBoxLayout(self)
        self.button_layout = QVBoxLayout()
        self.button_container = QFrame()
        self.panel_container = QFrame()
        self.stacked_widget = QStackedWidget()
        self.splitter = QSplitter()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the sidebar UI."""
        # Configure main layout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Configure button container
        self.button_container.setFixedWidth(50)
        self.button_container.setFrameStyle(QFrame.Shape.StyledPanel)
        self.button_container.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-right: 1px solid #404040;
            }
        """)
        
        # Set button layout on container
        self.button_container.setLayout(self.button_layout)
        self.button_layout.setContentsMargins(5, 5, 5, 5)
        self.button_layout.setSpacing(2)
        self.button_layout.addStretch()  # Push buttons to top
        
        # Configure panel container
        self.panel_container.setMinimumWidth(200)
        self.panel_container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        panel_layout = QVBoxLayout(self.panel_container)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(self.stacked_widget)
        
        # Add to main layout
        self.main_layout.addWidget(self.button_container)
        self.main_layout.addWidget(self.panel_container)
        
        # Initially hide panel container
        self.panel_container.hide()
        
    def add_button(self, panel_id: str, text: str, icon_path: Optional[str] = None) -> SidebarButton:
        """Add a button to the sidebar.
        
        Args:
            panel_id: Unique ID for the panel
            text: Button text
            icon_path: Optional icon path
            
        Returns:
            The created button
        """
        if panel_id in self.buttons:
            return self.buttons[panel_id]
            
        button = SidebarButton(text, icon_path)
        button.set_panel_id(panel_id)
        button.clicked.connect(lambda: self._on_button_clicked(panel_id))
        
        self.buttons[panel_id] = button
        
        # Insert before the stretch
        button_count = len(self.buttons) - 1
        self.button_layout.insertWidget(button_count, button)
        
        return button
        
    def add_panel(self, panel_id: str, panel: AbstractPanel):
        """Add a panel to the sidebar.
        
        Args:
            panel_id: Unique ID for the panel
            panel: Panel widget to add
        """
        if panel_id in self.panels:
            return
            
        self.panels[panel_id] = panel
        self.stacked_widget.addWidget(panel)
        
    def remove_panel(self, panel_id: str):
        """Remove a panel from the sidebar.
        
        Args:
            panel_id: ID of panel to remove
        """
        if panel_id not in self.panels:
            return
            
        panel = self.panels[panel_id]
        self.stacked_widget.removeWidget(panel)
        del self.panels[panel_id]
        
        if panel_id in self.buttons:
            button = self.buttons[panel_id]
            self.button_layout.removeWidget(button)
            button.deleteLater()
            del self.buttons[panel_id]
            
        if self.current_panel_id == panel_id:
            self.current_panel_id = ""
            self.panel_container.hide()
            
    def show_panel(self, panel_id: str):
        """Show a specific panel.
        
        Args:
            panel_id: ID of panel to show
        """
        if panel_id not in self.panels:
            return
            
        # Deactivate all buttons
        for button in self.buttons.values():
            button.set_active(False)
            
        # Activate the selected button
        if panel_id in self.buttons:
            self.buttons[panel_id].set_active(True)
            
        # Show the panel
        panel = self.panels[panel_id]
        self.stacked_widget.setCurrentWidget(panel)
        self.panel_container.show()
        self.current_panel_id = panel_id
        
        self.panel_requested.emit(panel_id)
        
    def hide_panel(self):
        """Hide the current panel."""
        # Deactivate all buttons
        for button in self.buttons.values():
            button.set_active(False)
            
        self.panel_container.hide()
        current_id = self.current_panel_id
        self.current_panel_id = ""
        
        if current_id:
            self.panel_hidden.emit(current_id)
            
    def toggle_panel(self, panel_id: str):
        """Toggle a panel's visibility.
        
        Args:
            panel_id: ID of panel to toggle
        """
        if self.current_panel_id == panel_id:
            self.hide_panel()
        else:
            self.show_panel(panel_id)
            
    def _on_button_clicked(self, panel_id: str):
        """Handle button click.
        
        Args:
            panel_id: ID of the clicked panel
        """
        self.toggle_panel(panel_id)
        
    def get_current_panel_id(self) -> str:
        """Get the currently visible panel ID.
        
        Returns:
            Current panel ID or empty string
        """
        return self.current_panel_id
        
    def get_panel(self, panel_id: str) -> Optional[AbstractPanel]:
        """Get a panel by ID.
        
        Args:
            panel_id: Panel ID
            
        Returns:
            Panel instance or None
        """
        return self.panels.get(panel_id)
        
    def set_sidebar_width(self, width: int):
        """Set the width of the sidebar panel area.
        
        Args:
            width: Width in pixels
        """
        self.sidebar_width = width
        self.panel_container.setFixedWidth(width)
