#!/usr/bin/env python3
"""
Test cases for view modes and column support in the enhanced file explorer.
"""
import sys
import os
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QDir, QTimer, Qt, QItemSelectionModel
from PySide6.QtTest import QTest
from PySide6.QtGui import QAction

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).parents[3]))

from plugins.core.file_explorer.enhanced_plugin import (
    FileExplorerWidget, 
    FileExplorerPanel
)

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

class TestViewModes:
    """Tests for view mode switching."""
    
    def test_initial_view_mode(self, explorer_widget):
        """Test the default view mode."""
        assert explorer_widget.view_mode == "list"
        assert explorer_widget.tree_view.iconSize().width() == 16
        
    def test_list_view_mode(self, explorer_widget):
        """Test setting list view mode."""
        explorer_widget._set_view_mode("list")
        assert explorer_widget.view_mode == "list"
        assert explorer_widget.tree_view.iconSize().width() == 16
        assert explorer_widget.tree_view.isRootDecorated() is True
        
    def test_icons_view_mode(self, explorer_widget):
        """Test setting icons view mode."""
        explorer_widget._set_view_mode("icons")
        assert explorer_widget.view_mode == "icons"
        assert explorer_widget.tree_view.iconSize().width() == 32
        assert explorer_widget.tree_view.isRootDecorated() is False
        
    def test_columns_view_mode(self, explorer_widget):
        """Test setting columns view mode."""
        explorer_widget._set_view_mode("columns")
        assert explorer_widget.view_mode == "columns"
        # Check if all columns are visible
        header = explorer_widget.tree_view.header()
        for i in range(explorer_widget.file_model.columnCount()):
            assert not header.isSectionHidden(i)
        
    def test_gallery_view_mode(self, explorer_widget):
        """Test setting gallery view mode."""
        explorer_widget._set_view_mode("gallery")
        assert explorer_widget.view_mode == "gallery"
        assert explorer_widget.tree_view.iconSize().width() == 48
        # Check if only name column is visible
        header = explorer_widget.tree_view.header()
        assert not header.isSectionHidden(0)  # Name column should be visible
        for i in range(1, explorer_widget.file_model.columnCount()):
            assert header.isSectionHidden(i)

class TestColumnManagement:
    """Tests for column visibility and sorting."""
    
    def test_toggle_column(self, explorer_widget):
        """Test toggling column visibility."""
        # Initially, only name and size should be visible
        header = explorer_widget.tree_view.header()
        assert not header.isSectionHidden(0)  # Name
        assert not header.isSectionHidden(1)  # Size
        assert header.isSectionHidden(2)      # Type
        assert header.isSectionHidden(3)      # Date Modified
        
        # Toggle Type column
        explorer_widget._toggle_column("kind", 2)
        assert not header.isSectionHidden(2)  # Now visible
        
        # Toggle it off again
        explorer_widget._toggle_column("kind", 2)
        assert header.isSectionHidden(2)      # Hidden again
        
    def test_column_active_list(self, explorer_widget):
        """Test active columns list updates."""
        assert "name" in explorer_widget.active_columns
        assert "size" in explorer_widget.active_columns
        assert "kind" not in explorer_widget.active_columns
        
        # Add a column
        explorer_widget._toggle_column("kind", 2)
        assert "kind" in explorer_widget.active_columns
        
        # Remove a column
        explorer_widget._toggle_column("size", 1)
        assert "size" not in explorer_widget.active_columns

class TestSorting:
    """Tests for sorting functionality."""
    
    def test_default_sort(self, explorer_widget):
        """Test default sort settings."""
        assert explorer_widget.current_sort_column == 0  # Name
        assert explorer_widget.current_sort_order == Qt.SortOrder.AscendingOrder
        
    def test_set_sort_column(self, explorer_widget):
        """Test changing sort column."""
        explorer_widget._set_sort_column(1)  # Sort by size
        assert explorer_widget.current_sort_column == 1
        
    def test_set_sort_order(self, explorer_widget):
        """Test changing sort order."""
        explorer_widget._set_sort_order(Qt.SortOrder.DescendingOrder)
        assert explorer_widget.current_sort_order == Qt.SortOrder.DescendingOrder

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
    
    # Add a timer to switch view modes for demonstration
    def cycle_view_modes():
        current_mode = explorer.explorer_widget.view_mode
        if current_mode == "list":
            explorer.explorer_widget._set_view_mode("icons")
            print("Switched to Icons View")
        elif current_mode == "icons":
            explorer.explorer_widget._set_view_mode("columns")
            print("Switched to Columns View")
        elif current_mode == "columns":
            explorer.explorer_widget._set_view_mode("gallery")
            print("Switched to Gallery View")
        else:
            explorer.explorer_widget._set_view_mode("list")
            print("Switched to List View")
    
    # Uncomment to enable view mode cycling every 3 seconds
    # timer = QTimer()
    # timer.timeout.connect(cycle_view_modes)
    # timer.start(3000)
    
    if not existing_app:
        sys.exit(app.exec())
        
if __name__ == "__main__":
    # Manual test runner
    run_standalone_test()
