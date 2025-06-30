"""
Abstract Panel - Base class for all dockable panels.
"""

from PySide6.QtWidgets import QDockWidget, QWidget
from PySide6.QtCore import Qt, Signal


class AbstractPanel(QDockWidget):
    """Base class for all dockable panels in the PO Editor."""
    
    # Signals
    panel_activated = Signal(str)  # Emitted when panel becomes active
    panel_deactivated = Signal(str)  # Emitted when panel becomes inactive
    
    def __init__(self, title: str, parent=None):
        """Initialize the abstract panel.
        
        Args:
            title: The title of the panel
            parent: Parent widget
        """
        super().__init__(title, parent)
        
        self.panel_id = None  # Will be set by the plugin manager
        self._setup_panel()
        
    def _setup_panel(self):
        """Set up the panel properties."""
        # Allow the panel to be docked on any side
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea | 
            Qt.DockWidgetArea.TopDockWidgetArea | 
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        
        # Enable floating
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
    def set_panel_id(self, panel_id: str):
        """Set the unique panel ID.
        
        Args:
            panel_id: Unique identifier for this panel
        """
        self.panel_id = panel_id
        
    def get_panel_id(self) -> str:
        """Get the panel ID.
        
        Returns:
            The unique panel identifier
        """
        return self.panel_id or ""
        
    def activate_panel(self):
        """Activate the panel (bring to front, show, etc.)."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.panel_activated.emit(self.panel_id or "unknown")
        
    def deactivate_panel(self):
        """Deactivate the panel."""
        self.panel_deactivated.emit(self.panel_id or "unknown")
        
    def get_state(self) -> dict:
        """Get the current state of the panel for saving.
        
        Returns:
            Dictionary containing panel state
        """
        return {
            "visible": self.isVisible(),
            "floating": self.isFloating(),
            "geometry": {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height()
            }
        }
        
    def restore_state(self, state: dict):
        """Restore the panel state.
        
        Args:
            state: Dictionary containing panel state
        """
        if "visible" in state:
            self.setVisible(state["visible"])
            
        if "floating" in state:
            self.setFloating(state["floating"])
            
        if "geometry" in state:
            geom = state["geometry"]
            self.setGeometry(geom["x"], geom["y"], geom["width"], geom["height"])
            
    def closeEvent(self, event):
        """Handle panel close event."""
        self.deactivate_panel()
        super().closeEvent(event)
