#!/usr/bin/env python3
"""
PO Editor - A modern gettext PO file editor with plugin support
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.main_frame import MainFrame
from core.plugin_manager import PluginManager
from core.database_manager import DatabaseManager
from styles.vscode_theme import GLOBAL_STYLESHEET


def main():
    """Main entry point for the PO Editor application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PO Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PO Editor Team")
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.initialize()
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    
    # Create main window
    main_window = MainFrame(plugin_manager, db_manager)
    
    # Load plugins
    plugin_manager.set_main_window(main_window)
    plugin_manager.discover_and_load_plugins()
    
    # Show main window
    main_window.show()
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
