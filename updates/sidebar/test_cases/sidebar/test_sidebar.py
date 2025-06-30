"""
Test cases for Sidebar Plugin
"""

import sys
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from plugins.core.sidebar.plugin import SidebarButton, SidebarContentArea, SidebarPanel, SidebarPlugin


class TestSidebarButton:
    """Test cases for SidebarButton class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture  
    def button(self, app):
        """Create a SidebarButton instance."""
        return SidebarButton("Test", "test_icon")
        
    def test_button_initialization(self, button):
        """Test button initialization."""
        assert button.text_value == "Test"
        assert button.icon_name == "test_icon"
        assert button.is_active == False
        assert button.isCheckable() == True
        
    def test_button_set_active(self, button):
        """Test setting button active state."""
        button.set_active(True)
        assert button.is_active == True
        assert button.isChecked() == True
        
        button.set_active(False)
        assert button.is_active == False
        assert button.isChecked() == False
        
    def test_button_size(self, button):
        """Test button has correct size."""
        size = button.size()
        assert size.width() == 50
        assert size.height() == 50


class TestSidebarContentArea:
    """Test cases for SidebarContentArea class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def content_area(self, app):
        """Create a SidebarContentArea instance."""
        return SidebarContentArea()
        
    def test_content_area_initialization(self, content_area):
        """Test content area initialization."""
        assert content_area.current_panel is None
        assert content_area.panels == {}
        assert content_area.stacked_widget is not None
        
    def test_add_panel(self, content_area):
        """Test adding a panel."""
        test_widget = QWidget()
        content_area.add_panel("test_panel", test_widget)
        
        assert "test_panel" in content_area.panels
        assert content_area.panels["test_panel"] == test_widget
        
    def test_show_panel(self, content_area):
        """Test showing a panel."""
        test_widget = QWidget()
        content_area.add_panel("test_panel", test_widget)
        content_area.show_panel("test_panel")
        
        assert content_area.current_panel == "test_panel"
        assert content_area.stacked_widget.currentWidget() == test_widget


class TestSidebarPanel:
    """Test cases for SidebarPanel class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def sidebar_panel(self, app):
        """Create a SidebarPanel instance."""
        return SidebarPanel()
        
    def test_sidebar_panel_initialization(self, sidebar_panel):
        """Test sidebar panel initialization."""
        assert sidebar_panel.buttons == {}
        assert sidebar_panel.content_area is not None
        assert sidebar_panel.current_active_button is None
        assert sidebar_panel.sidebar_visible == True
        
    def test_add_sidebar_item(self, sidebar_panel):
        """Test adding a sidebar item."""
        test_widget = QWidget()
        sidebar_panel.add_sidebar_item("test_item", "Test Item", test_widget)
        
        assert "test_item" in sidebar_panel.buttons
        assert "test_item" in sidebar_panel.content_area.panels
        
    def test_get_active_panel(self, sidebar_panel):
        """Test getting active panel."""
        assert sidebar_panel.get_active_panel() is None
        
        # Add item and activate it
        test_widget = QWidget()
        sidebar_panel.add_sidebar_item("test_item", "Test Item", test_widget)
        sidebar_panel.set_active_panel("test_item")
        
        assert sidebar_panel.get_active_panel() == "test_item"


class TestSidebarPlugin:
    """Test cases for SidebarPlugin class."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def plugin(self, app):
        """Create a SidebarPlugin instance."""
        return SidebarPlugin("sidebar")
        
    def test_plugin_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.name == "sidebar"
        assert plugin.version == "1.0.0"
        assert plugin.sidebar_panel is None
        
    def test_plugin_load(self, plugin):
        """Test plugin loading."""
        success = plugin.load()
        assert success == True
        assert plugin.sidebar_panel is not None
        
    def test_plugin_unload(self, plugin):
        """Test plugin unloading."""
        plugin.load()
        success = plugin.unload()
        assert success == True
        assert plugin.sidebar_panel is None
        
    def test_get_panels(self, plugin):
        """Test getting plugin panels."""
        # Before loading
        panels = plugin.get_panels()
        assert panels == []
        
        # After loading
        plugin.load()
        panels = plugin.get_panels()
        assert len(panels) == 1
        assert panels[0] == plugin.sidebar_panel


if __name__ == "__main__":
    pytest.main([__file__])
