"""
Global stylesheet for PO Editor application
VS Code-like dark theme
"""

GLOBAL_STYLESHEET = """
/* Main Application */
QMainWindow {
    background-color: #1e1e1e;
    color: #cccccc;
}

/* Sidebar Components */
#SidebarButton {
    border: none;
    background-color: #2d2d30;
    color: #cccccc;
    padding: 0px;
    margin: 1px;
    border-radius: 2px;
}

#SidebarButton:hover {
    background-color: #37373d;
}

#SidebarButton:checked {
    background-color: #094771;
    border-left: 2px solid #007acc;
}

#SidebarButton:pressed {
    background-color: #005a9e;
}

/* Sidebar Panel */
#SidebarButtonStrip {
    background-color: #2d2d30;
    border-right: 1px solid #3e3e42;
}

/* Content Area */
#SidebarContentArea {
    background-color: #252526;
    border-right: 1px solid #3e3e42;
    min-width: 200px;
}

/* Stacked Widget inside Content Area */
QStackedWidget {
    background-color: #252526;
    border: none;
}

/* File Explorer */
QTreeView {
    background-color: #252526;
    color: #cccccc;
    border: none;
    selection-background-color: #094771;
    alternate-background-color: #2a2d2e;
}

QTreeView::item {
    padding: 4px;
    border: none;
}

QTreeView::item:hover {
    background-color: #2a2d2e;
}

QTreeView::item:selected {
    background-color: #094771;
}

QTreeView::branch {
    background-color: transparent;
}

/* Toolbar */
QWidget#toolbar {
    background-color: #252526;
    border-bottom: 1px solid #3e3e42;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #005a9e;
}

/* Sidebar Content Buttons */
#SidebarContentButton {
    background-color: #2d2d30;
    color: #cccccc;
    border: 1px solid #3e3e42;
    padding: 8px 16px;
    border-radius: 3px;
    text-align: left;
    font-size: 13px;
    min-width: 120px;
}

#SidebarContentButton:hover {
    background-color: #37373d;
    border-color: #007acc;
}

#SidebarContentButton:pressed {
    background-color: #094771;
}

/* Line Edit */
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3e3e42;
    padding: 4px;
    border-radius: 2px;
}

QLineEdit:focus {
    border: 1px solid #007acc;
}

/* Text Edit */
QTextEdit {
    background-color: #1e1e1e;
    color: #cccccc;
    border: 1px solid #3e3e42;
    selection-background-color: #094771;
}

/* Menu Bar */
QMenuBar {
    background-color: #2d2d30;
    color: #cccccc;
    border-bottom: 1px solid #3e3e42;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 8px;
}

QMenuBar::item:selected {
    background-color: #094771;
}

/* Menu */
QMenu {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
}

QMenu::item {
    padding: 4px 20px;
}

QMenu::item:selected {
    background-color: #094771;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: white;
    border-top: 1px solid #3e3e42;
}

/* Dock Widget */
QDockWidget {
    color: #cccccc;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}

QDockWidget::title {
    background-color: #2d2d30;
    padding: 4px;
    border-bottom: 1px solid #3e3e42;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #252526;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #424242;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4f4f4f;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    background-color: #252526;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #424242;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4f4f4f;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
"""
