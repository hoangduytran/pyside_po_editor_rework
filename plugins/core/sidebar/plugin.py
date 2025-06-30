"""
Sidebar Plugin - Core plugin that provides the main sidebar with navigation buttons.
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPainter, QPen

from core.plugin_manager import Plugin
from core.abstract_panel import AbstractPanel

# Import the resources
import resources_rc

# Import the generated resources
try:
    import resources_rc
except ImportError:
    print("Warning: Could not import resources_rc. Icons may not display correctly.")


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation."""
    
    def __init__(self, text: str, icon_name: Optional[str] = None, parent=None):
        """Initialize the sidebar button.
        
        Args:
            text: Button text
            icon_name: Optional icon name
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        # Initialize all attributes in __init__
        self.is_active = False
        self.icon_name = icon_name or ""
        self.text_value = text
        
        self._setup_button()
        
    def _setup_button(self):
        """Set up the button appearance and behavior."""
        self.setCheckable(True)
        self.setFixedSize(QSize(48, 48))
        
        # Set icon if icon_name is provided
        if self.icon_name:
            icon_path = f":/icons/resources/icons/{self.icon_name}.png"
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(24, 24))
        
        # Set tooltip instead of text
        self.setToolTip(self.text_value)
        
        # Remove text from button (icon only)
        self.setText("")
        
        # Set object name for styling
        self.setObjectName("SidebarButton")
        
    def set_active(self, active: bool):
        """Set the button active state.
        
        Args:
            active: Whether button should be active
        """
        self.is_active = active
        self.setChecked(active)


class SidebarContentArea(QWidget):
    """Content area that displays the selected sidebar panel."""
    
    def __init__(self, parent=None):
        """Initialize the content area."""
        super().__init__(parent)
        
        # Initialize all attributes in __init__
        self.current_panel = None
        self.panels = {}
        self.stacked_widget = QStackedWidget()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the content area UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        
    def add_panel(self, panel_id: str, panel: QWidget):
        """Add a panel to the content area.
        
        Args:
            panel_id: Unique panel identifier
            panel: Panel widget to add
        """
        self.panels[panel_id] = panel
        self.stacked_widget.addWidget(panel)
        
    def show_panel(self, panel_id: str):
        """Show a specific panel.
        
        Args:
            panel_id: Panel identifier to show
        """
        if panel_id in self.panels:
            panel = self.panels[panel_id]
            self.stacked_widget.setCurrentWidget(panel)
            self.current_panel = panel_id
            
    def hide_current_panel(self):
        """Hide the current panel."""
        self.current_panel = None
        # Create empty widget to show when nothing is selected
        empty_widget = QWidget()
        self.stacked_widget.setCurrentWidget(empty_widget)


class SidebarPanel(AbstractPanel):
    """Main sidebar panel with navigation buttons and content area."""
    
    # Signals
    panel_requested = Signal(str)  # Panel ID requested
    panel_toggled = Signal(str, bool)  # Panel ID, visibility state
    
    def __init__(self, parent=None):
        """Initialize the sidebar panel."""
        super().__init__("Sidebar", parent)
        
        # Initialize all attributes in __init__
        self.buttons = {}
        self.content_area = SidebarContentArea()
        self.button_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        self.buttons_widget = QWidget()
        self.current_active_button = None
        self.sidebar_visible = True
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the sidebar UI."""
        # Main widget
        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create buttons widget (vertical strip)
        self.buttons_widget = QWidget()
        self.buttons_widget.setFixedWidth(50)
        self.buttons_widget.setObjectName("SidebarButtonStrip")
        
        self.button_layout = QVBoxLayout(self.buttons_widget)
        self.button_layout.setContentsMargins(1, 8, 1, 8)
        self.button_layout.setSpacing(2)
        self.button_layout.addStretch()  # Push buttons to top
        
        # Create content area (already initialized in __init__)
        self.content_area.setFixedWidth(250)
        self.content_area.setObjectName("SidebarContentArea")
        
        # Add to main layout
        self.main_layout.addWidget(self.buttons_widget)
        self.main_layout.addWidget(self.content_area)
        
        self.setWidget(main_widget)
        
        # Set initial size
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        
    def add_sidebar_item(self, item_id: str, text: str, panel_widget: QWidget, icon_name: Optional[str] = None):
        """Add an item to the sidebar.
        
        Args:
            item_id: Unique identifier for the item
            text: Display text for the button
            panel_widget: Widget to show when button is clicked
            icon_name: Optional icon name
        """
        # Create button
        button = SidebarButton(text, icon_name)
        button.clicked.connect(lambda: self._on_button_clicked(item_id))
        
        # Store button and add to layout
        self.buttons[item_id] = button
        
        # Insert before the stretch (second to last position)
        button_count = self.button_layout.count()
        self.button_layout.insertWidget(button_count - 1, button)
        
        # Add panel to content area
        self.content_area.add_panel(item_id, panel_widget)
        
    def _on_button_clicked(self, item_id: str):
        """Handle button click.
        
        Args:
            item_id: ID of the clicked button
        """
        button = self.buttons[item_id]
        
        # If clicking the same button that's already active, toggle visibility
        if self.current_active_button == item_id and self.sidebar_visible:
            self._hide_sidebar_content()
            return
            
        # Deactivate previous button
        if self.current_active_button and self.current_active_button in self.buttons:
            self.buttons[self.current_active_button].set_active(False)
            
        # Activate new button and show content
        button.set_active(True)
        self.current_active_button = item_id
        self._show_sidebar_content(item_id)
        
    def _show_sidebar_content(self, panel_id: str):
        """Show sidebar content for the given panel.
        
        Args:
            panel_id: Panel to show
        """
        self.content_area.show_panel(panel_id)
        self.content_area.setVisible(True)
        self.sidebar_visible = True
        self.panel_toggled.emit(panel_id, True)
        
    def _hide_sidebar_content(self):
        """Hide the sidebar content area."""
        self.content_area.setVisible(False)
        self.sidebar_visible = False
        
        # Deactivate current button
        if self.current_active_button and self.current_active_button in self.buttons:
            self.buttons[self.current_active_button].set_active(False)
            self.current_active_button = None
            
        self.panel_toggled.emit("", False)
        
    def get_active_panel(self) -> Optional[str]:
        """Get the currently active panel ID.
        
        Returns:
            Active panel ID or None
        """
        return self.current_active_button
        
    def set_active_panel(self, panel_id: str):
        """Set the active panel programmatically.
        
        Args:
            panel_id: Panel ID to activate
        """
        if panel_id in self.buttons:
            self._on_button_clicked(panel_id)


class SidebarPlugin(Plugin):
    """Sidebar plugin implementation."""
    
    def __init__(self, name: str):
        """Initialize the plugin."""
        super().__init__(name, "1.0.0")
        
        # Initialize all attributes in __init__
        self.sidebar_panel = None
        
    def load(self) -> bool:
        """Load the sidebar plugin."""
        try:
            self.sidebar_panel = SidebarPanel()
            
            # Add default panels
            self._add_default_panels()
            
            print("Sidebar plugin loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load Sidebar plugin: {e}")
            return False
            
    def unload(self) -> bool:
        """Unload the sidebar plugin."""
        try:
            if self.sidebar_panel:
                self.sidebar_panel.close()
                self.sidebar_panel = None
            print("Sidebar plugin unloaded successfully")
            return True
        except Exception as e:
            print(f"Failed to unload Sidebar plugin: {e}")
            return False
            
    def get_panels(self):
        """Get panels provided by this plugin."""
        return [self.sidebar_panel] if self.sidebar_panel else []
        
    def _add_default_panels(self):
        """Add default panels to the sidebar."""
        try:
            # Import the enhanced file explorer widget
            import sys
            from pathlib import Path
            
            # Add the plugins directory to path for importing
            plugins_dir = Path(__file__).parent.parent.parent
            if str(plugins_dir) not in sys.path:
                sys.path.insert(0, str(plugins_dir))
            
            from plugins.core.file_explorer.enhanced_plugin import FileExplorerWidget
            
            # Create real file explorer widget
            explorer_widget = FileExplorerWidget()
        except ImportError as e:
            print(f"Could not import FileExplorerWidget: {e}")
            # Fallback to simple explorer
            from PySide6.QtWidgets import QTreeView, QFileSystemModel
            from PySide6.QtCore import QDir
            
            explorer_widget = QWidget()
            layout = QVBoxLayout(explorer_widget)
            
            tree_view = QTreeView()
            file_model = QFileSystemModel()
            file_model.setRootPath(QDir.currentPath())
            tree_view.setModel(file_model)
            tree_view.setRootIndex(file_model.index(QDir.currentPath()))
            tree_view.hideColumn(1)
            tree_view.hideColumn(2)
            tree_view.hideColumn(3)
            
            layout.addWidget(tree_view)
        
        # Search placeholder  
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_button = QPushButton("Search in Files")
        search_button.setObjectName("SidebarContentButton")
        search_layout.addWidget(search_button)
        search_layout.addStretch()
        
        # Add debug panel
        debug_widget = QWidget()
        debug_layout = QVBoxLayout(debug_widget)
        debug_button = QPushButton("Start Debugging")
        debug_button.setObjectName("SidebarContentButton")
        debug_layout.addWidget(debug_button)
        debug_layout.addStretch()
        
        # Add extensions panel
        extensions_widget = QWidget()
        extensions_layout = QVBoxLayout(extensions_widget)
        extensions_button = QPushButton("Browse Extensions")
        extensions_button.setObjectName("SidebarContentButton")
        extensions_layout.addWidget(extensions_button)
        extensions_layout.addStretch()
        
        # Add settings panel
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_button = QPushButton("Open Settings")
        settings_button.setObjectName("SidebarContentButton")
        settings_layout.addWidget(settings_button)
        settings_layout.addStretch()
        
        # Add to sidebar
        if self.sidebar_panel:
            self.sidebar_panel.add_sidebar_item("explorer", "File Explorer", explorer_widget, "explorer")
            self.sidebar_panel.add_sidebar_item("search", "Search", search_widget, "search")
            self.sidebar_panel.add_sidebar_item("debug", "Run & Debug", debug_widget, "debug")
            self.sidebar_panel.add_sidebar_item("extensions", "Extensions", extensions_widget, "extensions")
            self.sidebar_panel.add_sidebar_item("settings", "Settings", settings_widget, "settings")
            
            # Set Explorer as the default active panel
            self.sidebar_panel.set_active_panel("explorer")
            
    def get_sidebar_panel(self) -> Optional[SidebarPanel]:
        """Get the sidebar panel instance.
        
        Returns:
            Sidebar panel or None
        """
        return self.sidebar_panel
