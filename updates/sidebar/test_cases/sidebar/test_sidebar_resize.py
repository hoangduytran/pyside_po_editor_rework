#!/usr/bin/env python3
"""
Test the sidebar resizing behavior
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import resources and styling
import resources_rc
from styles.vscode_theme import GLOBAL_STYLESHEET
from plugins.core.sidebar.plugin import SidebarPanel

class ResizeTestWindow(QMainWindow):
    """Test window to verify sidebar resizing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sidebar Resize Test - PO Editor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Apply stylesheet
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        self.sidebar = SidebarPanel()
        self.sidebar.setObjectName("TestSidebar")
        
        # Add mock panels to sidebar
        self._setup_sidebar_panels()
        
        # Create main content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1e1e1e; border-left: 1px solid #3e3e42;")
        content_layout = QVBoxLayout(content_widget)
        
        # Add title
        title = QLabel("Main Content Area")
        title.setStyleSheet("color: #cccccc; font-size: 18px; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        # Add instructions
        instructions = QLabel("""
        Instructions for testing sidebar resizing:
        
        1. Try dragging the sidebar edge to resize it
        2. Notice how the content area expands/contracts
        3. Switch between different sidebar panels
        4. Verify that all panels resize properly
        5. Check minimum and maximum size constraints
        """)
        instructions.setStyleSheet("color: #cccccc; padding: 20px; line-height: 1.5;")
        instructions.setWordWrap(True)
        content_layout.addWidget(instructions)
        
        content_layout.addStretch()
        
        # Add widgets to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_widget)
        
        # Set initial proportions
        main_layout.setStretchFactor(self.sidebar, 0)      # Fixed initial size
        main_layout.setStretchFactor(content_widget, 1)   # Expandable
        
        print("Resize test window created successfully!")
        print("Try resizing the sidebar to test the new functionality.")
        
    def _setup_sidebar_panels(self):
        """Set up test panels for the sidebar"""
        # Create test panels with different content
        
        # Panel 1: Simple text
        panel1 = QWidget()
        panel1.setSizePolicy(panel1.sizePolicy().horizontalPolicy(), panel1.sizePolicy().verticalPolicy())
        layout1 = QVBoxLayout(panel1)
        layout1.addWidget(QLabel("Panel 1 Content"))
        layout1.addWidget(QPushButton("Button 1"))
        layout1.addStretch()
        
        # Panel 2: Multiple buttons
        panel2 = QWidget()
        layout2 = QVBoxLayout(panel2)
        for i in range(5):
            btn = QPushButton(f"Resizable Button {i+1}")
            btn.setObjectName("SidebarContentButton")
            layout2.addWidget(btn)
        layout2.addStretch()
        
        # Panel 3: Text area
        panel3 = QWidget()
        layout3 = QVBoxLayout(panel3)
        text_label = QLabel("This panel tests text wrapping and resizing behavior. " * 10)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #cccccc; padding: 10px;")
        layout3.addWidget(text_label)
        layout3.addStretch()
        
        # Add panels to sidebar
        self.sidebar.add_sidebar_item("test1", "Test Panel 1", panel1, "explorer")
        self.sidebar.add_sidebar_item("test2", "Test Panel 2", panel2, "search")
        self.sidebar.add_sidebar_item("test3", "Test Panel 3", panel3, "debug")
        
        # Set default active panel
        self.sidebar.set_active_panel("test1")

def main():
    app = QApplication(sys.argv)
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    window = ResizeTestWindow()
    window.show()
    
    print("Sidebar resize test started.")
    print("Drag the sidebar edge to test resizing functionality.")
    print("Press Ctrl+C in terminal to close.")
    
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nResize test completed.")
        sys.exit(0)
