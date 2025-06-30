#!/usr/bin/env python3
"""
Test the custom icons and sidebar styling
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import resources and styling
import resources_rc
from styles.vscode_theme import GLOBAL_STYLESHEET
from plugins.core.sidebar.plugin import SidebarButton

class IconTestWindow(QMainWindow):
    """Test window to verify icons are working"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Test - PO Editor Sidebar")
        self.setGeometry(100, 100, 600, 400)
        
        # Apply stylesheet
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Test the sidebar buttons
        button_layout = QHBoxLayout()
        
        icons = [
            ("explorer", "File Explorer"),
            ("search", "Search"),
            ("debug", "Run & Debug"),
            ("extensions", "Extensions"),
            ("settings", "Settings")
        ]
        
        for icon_name, tooltip in icons:
            button = SidebarButton(tooltip, icon_name)
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        print("Icon test window created successfully!")
        print("Icons being tested:", [icon[0] for icon in icons])

def main():
    app = QApplication(sys.argv)
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    window = IconTestWindow()
    window.show()
    
    print("Test application started. Check the icons in the window.")
    print("Press Ctrl+C in terminal to close.")
    
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest completed.")
        sys.exit(0)
