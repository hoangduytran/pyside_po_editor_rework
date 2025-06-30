#!/usr/bin/env python3
"""
Test cases for the enhanced file explorer.
"""
import sys
import os
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QDir, QTimer, Qt, QItemSelectionModel
from PySide6.QtTest import QTest
from PySide6.QtGui import QClipboard

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).parents[3]))

from plugins.core.file_explorer.enhanced_plugin import (
    FileExplorerWidget, 
    NavigationHistory, 
    FileExplorerPanel
)

class TestNavigationHistory:
    """Tests for the NavigationHistory class."""

    def test_init(self):
        """Test initialization."""
        history = NavigationHistory(max_history=30)
        assert history.max_history == 30
        assert len(history.history) == 0
        assert history.current_index == -1
    
    def test_add_path(self):
        """Test adding paths."""
        history = NavigationHistory()
        history.add_path("/tmp")
        history.add_path("/home")
        history.add_path("/usr")
        
        assert len(history.history) == 3
        assert history.current_index == 2
        assert history.history == ["/tmp", "/home", "/usr"]
        
    def test_go_back_forward(self):
        """Test navigation back and forward."""
        history = NavigationHistory()
        history.add_path("/tmp")
        history.add_path("/home")
        history.add_path("/usr")
        
        assert history.go_back() == "/home"
        assert history.current_index == 1
        assert history.go_back() == "/tmp"
        assert history.current_index == 0
        assert history.go_back() is None
        assert history.current_index == 0
        
        assert history.go_forward() == "/home"
        assert history.current_index == 1
        assert history.go_forward() == "/usr"
        assert history.current_index == 2
        assert history.go_forward() is None
        assert history.current_index == 2
        
    def test_can_go_back_forward(self):
        """Test can_go_back and can_go_forward methods."""
        history = NavigationHistory()
        assert not history.can_go_back()
        assert not history.can_go_forward()
        
        history.add_path("/tmp")
        assert not history.can_go_back()
        assert not history.can_go_forward()
        
        history.add_path("/home")
        assert history.can_go_back()
        assert not history.can_go_forward()
        
        history.go_back()
        assert not history.can_go_back()
        assert history.can_go_forward()
        
    def test_max_history(self):
        """Test max history limit."""
        history = NavigationHistory(max_history=3)
        history.add_path("/path1")
        history.add_path("/path2")
        history.add_path("/path3")
        history.add_path("/path4")
        
        assert len(history.history) == 3
        assert history.history == ["/path2", "/path3", "/path4"]
        assert history.current_index == 2


@pytest.fixture
def app():
    """Provide a Qt application."""
    existing_app = QApplication.instance()
    if not existing_app:
        # Create a new application
        app = QApplication([])
        yield app
    else:
        # Use existing application
        yield existing_app
    

@pytest.fixture
def explorer_widget(app):
    """Provide a FileExplorerWidget."""
    widget = FileExplorerWidget()
    widget.show()
    yield widget
    widget.close()


class TestFileExplorerWidget:
    """Tests for the FileExplorerWidget."""
    
    def test_init(self, explorer_widget):
        """Test initialization."""
        assert explorer_widget is not None
        assert explorer_widget.current_path == QDir.currentPath()
        assert explorer_widget.path_edit.text() == QDir.currentPath()
        
    def test_set_root_path(self, explorer_widget):
        """Test setting root path."""
        # Use a path we know exists
        home_path = os.path.expanduser("~")
        explorer_widget.set_root_path(home_path)
        
        assert explorer_widget.current_path == home_path
        assert explorer_widget.path_edit.text() == home_path
        
    def test_navigation_history(self, explorer_widget):
        """Test navigation history."""
        # Use paths we know exist
        home_path = os.path.expanduser("~")
        tmp_path = "/tmp"
        if os.path.exists(tmp_path):
            # First path
            explorer_widget.set_root_path(home_path)
            # Second path
            explorer_widget.set_root_path(tmp_path)
            
            # Go back
            explorer_widget._go_back()
            assert explorer_widget.current_path == home_path
            
            # Go forward
            explorer_widget._go_forward()
            assert explorer_widget.current_path == tmp_path
        else:
            pytest.skip("Test requires /tmp directory")
            
    def test_go_up(self, explorer_widget):
        """Test going up a directory."""
        # Use a path we know has a parent
        nested_path = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.exists(nested_path):
            explorer_widget.set_root_path(nested_path)
            explorer_widget._go_up()
            
            assert explorer_widget.current_path == os.path.expanduser("~")
        else:
            pytest.skip("Test requires ~/Documents directory")


@pytest.fixture
def explorer_panel(app):
    """Provide a FileExplorerPanel."""
    panel = FileExplorerPanel()
    panel.show()
    yield panel
    panel.close()


class TestFileExplorerPanel:
    """Tests for the FileExplorerPanel."""
    
    def test_init(self, explorer_panel):
        """Test initialization."""
        assert explorer_panel is not None
        assert explorer_panel.windowTitle() == "File Explorer"
        
    def test_set_root_path(self, explorer_panel):
        """Test setting root path."""
        # Use a path we know exists
        home_path = os.path.expanduser("~")
        explorer_panel.set_root_path(home_path)
        
        assert explorer_panel.explorer_widget.current_path == home_path
        assert explorer_panel.windowTitle() == f"File Explorer - {os.path.basename(home_path)}"
        
    def test_navigation_methods(self, explorer_panel):
        """Test navigation methods."""
        explorer_panel.navigate_to_home()
        assert explorer_panel.explorer_widget.current_path == os.path.expanduser("~")
        
        # Only test root navigation if we're not on Windows
        if os.name != "nt":
            explorer_panel.navigate_to_root()
            assert explorer_panel.explorer_widget.current_path == "/"


def run_standalone_test():
    """Run a standalone test for manual testing."""
    existing_app = QApplication.instance()
    if not existing_app:
        app = QApplication(sys.argv)
    else:
        app = existing_app
        
    main_window = QMainWindow()
    explorer = FileExplorerPanel()
    main_window.setCentralWidget(explorer)
    main_window.resize(800, 600)
    main_window.show()
    
    if not existing_app:
        sys.exit(app.exec())
        
if __name__ == "__main__":
    # Manual test runner
    run_standalone_test()
