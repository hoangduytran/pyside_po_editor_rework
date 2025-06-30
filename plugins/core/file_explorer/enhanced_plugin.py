"""
Enhanced File Explorer Plugin - Integrates with sidebar system.
"""

from PySide6.QtWidgets import (
    QTreeView, QVBoxLayout, QWidget, QFileSystemModel, QHeaderView,
    QHBoxLayout, QPushButton, QLineEdit, QLabel, QMenu,
    QToolButton, QToolTip, QApplication, QAbstractItemView
)
from PySide6.QtCore import QDir, Signal, Qt, QPoint, QSize, QTimer, QUrl, QSettings
from PySide6.QtGui import QIcon, QCursor, QDesktopServices, QAction, QActionGroup
import os
import glob
import pathlib
from typing import List, Optional, Dict, Any


from core.plugin_manager import Plugin
from core.abstract_panel import AbstractPanel


class NavigationHistory:
    """Manages navigation history for the file explorer."""
    
    def __init__(self, max_history: int = 50):
        """Initialize the navigation history.
        
        Args:
            max_history: Maximum number of history entries
        """
        self.history: List[str] = []
        self.current_index: int = -1
        self.max_history: int = max_history
        
    def add_path(self, path: str) -> None:
        """Add a new path to the history.
        
        Args:
            path: Path to add to history
        """
        # Don't add if it's the same as current
        if self.history and self.current_index >= 0 and self.history[self.current_index] == path:
            return
            
        # If we navigated back and then to a new location,
        # remove the forward history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
            
        # Add the new path
        self.history.append(path)
        self.current_index = len(self.history) - 1
        
        # Trim if history exceeds max size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.current_index = len(self.history) - 1
    
    def go_back(self) -> Optional[str]:
        """Go back in history.
        
        Returns:
            Previous path or None if at beginning
        """
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def go_forward(self) -> Optional[str]:
        """Go forward in history.
        
        Returns:
            Next path or None if at end
        """
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def can_go_back(self) -> bool:
        """Check if we can go back in history.
        
        Returns:
            True if there's history to go back to
        """
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if we can go forward in history.
        
        Returns:
            True if there's history to go forward to
        """
        return self.current_index < len(self.history) - 1
        
    def get_current(self) -> Optional[str]:
        """Get the current path.
        
        Returns:
            Current path or None if history is empty
        """
        if self.current_index >= 0 and self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
        
    def get_history(self) -> List[str]:
        """Get the full history.
        
        Returns:
            List of history entries
        """
        return self.history.copy()


class FileExplorerWidget(QWidget):
    """Enhanced file explorer widget with toolbar and tree view."""
    
    # Signals
    file_selected = Signal(str)  # File path selected
    directory_changed = Signal(str)  # Directory changed
    
    def __init__(self, parent=None):
        """Initialize the file explorer widget."""
        super().__init__(parent)
        
        # Initialize all attributes in __init__
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.path_edit = QLineEdit()
        self.refresh_button = QToolButton()
        self.nav_button = QToolButton()
        self.settings = QSettings("POEditor", "Settings")
        self.navigation_history = NavigationHistory()
        
        # Store the current working directory at app launch
        self.app_launch_directory = os.getcwd()
        
        # Get home folder as default path
        default_path = os.path.expanduser("~")
        self.current_path = default_path
        
        # Try to get saved path from settings
        if self.settings.contains("explorer/current_path"):
            saved_path = self.settings.value("explorer/current_path")
            if saved_path and os.path.exists(str(saved_path)):
                self.current_path = str(saved_path)
        
        # Initialize settings with proper types
        self.show_hidden_files = False
        if self.settings.contains("explorer/show_hidden"):
            self.show_hidden_files = self.settings.value("explorer/show_hidden", type=bool)
        
        self.path_filter = ""
        
        # View mode (with safe fallback)
        self.view_mode = "list"
        if self.settings.contains("explorer/view_mode"):
            view_mode = self.settings.value("explorer/view_mode")
            if view_mode in ["list", "icons", "columns", "gallery"]:
                self.view_mode = str(view_mode)
        
        # Active columns
        self.active_columns = ["name", "size"]
        if self.settings.contains("explorer/active_columns"):
            columns = self.settings.value("explorer/active_columns")
            if isinstance(columns, list):
                self.active_columns = [str(col) for col in columns]
        
        # Sort settings
        self.current_sort_column = 0
        if self.settings.contains("explorer/sort_column"):
            try:
                self.current_sort_column = int(self.settings.value("explorer/sort_column"))
            except (ValueError, TypeError):
                pass
                
        self.current_sort_order = Qt.SortOrder.AscendingOrder
        self.sort_actions = []  # Will store sort actions for menu
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(300)  # 300ms debounce for filtering
        
        self._setup_ui()
        self._connect_signals()
        self._setup_sorting()
        self._load_history()
        
        # Apply the saved view mode after UI setup
        self._set_view_mode(self.view_mode)
        
        # Initialize with the current path 
        # Use direct model access first to ensure model is ready
        self.file_model.setRootPath(self.current_path)
        self.tree_view.setRootIndex(self.file_model.index(self.current_path))
        
        # Display basename in path editor
        basename = os.path.basename(self.current_path) or self.current_path
        self.path_edit.setText(basename)
        self.path_edit.setToolTip(self.current_path)
        
        # Apply sort settings
        if hasattr(self, 'current_sort_column'):
            self.tree_view.sortByColumn(self.current_sort_column, self.current_sort_order)
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar layout
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(3, 3, 3, 3)
        toolbar_layout.setSpacing(3)
        
        # Navigation button
        self.nav_button.setText("📁")
        self.nav_button.setToolTip("Navigation Options")
        self.nav_button.setFixedSize(32, 32)
        self.nav_button.setStyleSheet("font-size: 18px;")
        self.nav_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar_layout.addWidget(self.nav_button)
        
        # Path editing field
        self.path_edit.setPlaceholderText("Enter path...")
        toolbar_layout.addWidget(self.path_edit)
        
        # Refresh button
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("Refresh")
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.setStyleSheet("font-size: 18px;")
        toolbar_layout.addWidget(self.refresh_button)
        
        # Add toolbar to main layout
        layout.addLayout(toolbar_layout)
        
        # Set up the tree view
        self.tree_view.setModel(self.file_model)
        self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setAnimated(True)
        
        # Connect sorting signals and set up header context menu
        header = self.tree_view.header()
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)
        header.sortIndicatorChanged.connect(self._on_sort_changed)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_header_context_menu)
        
        # Hide type and date modified columns by default
        header.hideSection(2)  # Type
        header.hideSection(3)  # Date Modified
        
        layout.addWidget(self.tree_view)
        
        # Set up the navigation button menu
        self._setup_navigation_menu()
        
        # Set up the path edit context menu
        self._setup_path_context_menu()
        
        # Initialize navigation history with current path
        self.navigation_history.add_path(self.current_path)
        
    def _setup_navigation_menu(self):
        """Set up the navigation button dropdown menu."""
        nav_menu = QMenu(self)
        
        # Root action
        root_action = QAction("Root (/)", self)
        root_action.triggered.connect(lambda: self.navigate_to("/"))
        nav_menu.addAction(root_action)
        
        # Home action
        home_action = QAction(f"Home (~)", self)
        home_action.triggered.connect(lambda: self.navigate_to(os.path.expanduser("~")))
        nav_menu.addAction(home_action)
        
        # Up action (parent directory)
        up_action = QAction("Up (Parent Directory)", self)
        up_action.triggered.connect(self._go_up)
        nav_menu.addAction(up_action)
        
        nav_menu.addSeparator()
        
        # Previous (back) action
        self.back_action = QAction("Previous", self)
        self.back_action.triggered.connect(self._go_back)
        self.back_action.setEnabled(False)
        nav_menu.addAction(self.back_action)
        
        # Next (forward) action
        self.forward_action = QAction("Next", self)
        self.forward_action.triggered.connect(self._go_forward)
        self.forward_action.setEnabled(False)
        nav_menu.addAction(self.forward_action)
        
        nav_menu.addSeparator()
        
        # View submenu
        view_menu = nav_menu.addMenu("View")
        
        # Toggle hidden files
        hidden_action = QAction("Hidden Files", self)
        hidden_action.setCheckable(True)
        hidden_action.setChecked(bool(self.show_hidden_files))
        hidden_action.triggered.connect(self._toggle_hidden_files)
        view_menu.addAction(hidden_action)
        
        view_menu.addSeparator()
        
        # View mode options
        view_mode_group = QActionGroup(self)
        
        list_view_action = QAction("As List", self)
        list_view_action.setCheckable(True)
        list_view_action.setChecked(self.view_mode == "list")
        list_view_action.triggered.connect(lambda: self._set_view_mode("list"))
        view_mode_group.addAction(list_view_action)
        view_menu.addAction(list_view_action)
        
        icons_view_action = QAction("As Icon and Text", self)
        icons_view_action.setCheckable(True)
        icons_view_action.setChecked(self.view_mode == "icons")
        icons_view_action.triggered.connect(lambda: self._set_view_mode("icons"))
        view_mode_group.addAction(icons_view_action)
        view_menu.addAction(icons_view_action)
        
        columns_view_action = QAction("As Columns", self)
        columns_view_action.setCheckable(True)
        columns_view_action.setChecked(self.view_mode == "columns")
        columns_view_action.triggered.connect(lambda: self._set_view_mode("columns"))
        view_mode_group.addAction(columns_view_action)
        view_menu.addAction(columns_view_action)
        
        gallery_view_action = QAction("As Gallery", self)
        gallery_view_action.setCheckable(True)
        gallery_view_action.setChecked(self.view_mode == "gallery")
        gallery_view_action.triggered.connect(lambda: self._set_view_mode("gallery"))
        view_mode_group.addAction(gallery_view_action)
        view_menu.addAction(gallery_view_action)
        
        view_menu.addSeparator()
        
        # Column submenu
        columns_menu = view_menu.addMenu("Add Columns")
        
        # Date modified column
        date_mod_action = QAction("Date Modified", self)
        date_mod_action.setCheckable(True)
        date_mod_action.setChecked("date_modified" in self.active_columns)
        date_mod_action.triggered.connect(lambda: self._toggle_column("date_modified", 3))
        columns_menu.addAction(date_mod_action)
        
        # Date created column
        date_created_action = QAction("Date Created", self)
        date_created_action.setCheckable(True)
        date_created_action.setChecked("date_created" in self.active_columns)
        date_created_action.triggered.connect(lambda: self._toggle_column("date_created", 4))
        columns_menu.addAction(date_created_action)
        
        # Type column
        type_action = QAction("Kind", self)
        type_action.setCheckable(True)
        type_action.setChecked("kind" in self.active_columns)
        type_action.triggered.connect(lambda: self._toggle_column("kind", 2))
        columns_menu.addAction(type_action)
        
        # Size column
        size_action = QAction("Size", self)
        size_action.setCheckable(True)
        size_action.setChecked("size" in self.active_columns)
        size_action.triggered.connect(lambda: self._toggle_column("size", 1))
        columns_menu.addAction(size_action)
        
        self.nav_button.setMenu(nav_menu)
    
    def _setup_path_context_menu(self):
        """Set up the path editor context menu."""
        self.path_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.path_edit.customContextMenuRequested.connect(self._show_path_context_menu)
    
    def _show_path_context_menu(self, pos):
        """Show the path editor context menu.
        
        Args:
            pos: Position for the context menu
        """
        context_menu = QMenu(self)
        
        # Copy operations
        copy_full_path = QAction("Copy Full Path", self)
        copy_full_path.triggered.connect(self._copy_full_path)
        context_menu.addAction(copy_full_path)
        
        copy_relative_path = QAction("Copy Relative Path", self)
        copy_relative_path.triggered.connect(self._copy_relative_path)
        context_menu.addAction(copy_relative_path)
        
        # Paste operations
        paste_path = QAction("Paste Path", self)
        paste_path.triggered.connect(self._paste_path)
        context_menu.addAction(paste_path)
        
        paste_env = QAction("Paste Environment Variables", self)
        paste_env.triggered.connect(self._paste_env_vars)
        context_menu.addAction(paste_env)
        
        context_menu.addSeparator()
        
        # Go To submenu
        goto_menu = context_menu.addMenu("Go To")
        
        root_action = QAction("Root", self)
        root_action.triggered.connect(lambda: self.navigate_to("/"))
        goto_menu.addAction(root_action)
        
        home_action = QAction("Home", self)
        home_action.triggered.connect(lambda: self.navigate_to(os.path.expanduser("~")))
        goto_menu.addAction(home_action)
        
        current_dir_action = QAction("Current Directory", self)
        current_dir_action.triggered.connect(lambda: self.navigate_to(self.app_launch_directory))
        current_dir_action.setToolTip(f"Go to application launch directory: {self.app_launch_directory}")
        goto_menu.addAction(current_dir_action)
        
        previous_action = QAction("Previous", self)
        previous_action.triggered.connect(self._go_back)
        previous_action.setEnabled(self.navigation_history.can_go_back())
        goto_menu.addAction(previous_action)
        
        next_action = QAction("Next", self)
        next_action.triggered.connect(self._go_forward)
        next_action.setEnabled(self.navigation_history.can_go_forward())
        goto_menu.addAction(next_action)
        
        context_menu.exec(self.path_edit.mapToGlobal(pos))
        
    def _show_header_context_menu(self, pos):
        """Show context menu for the header.
        
        Args:
            pos: Position for the context menu
        """
        context_menu = QMenu(self)
        
        # View submenu
        view_menu = context_menu.addMenu("View")
        
        # Toggle hidden files
        hidden_action = QAction("Hidden Files", self)
        hidden_action.setCheckable(True)
        hidden_action.setChecked(bool(self.show_hidden_files))
        hidden_action.triggered.connect(self._toggle_hidden_files)
        view_menu.addAction(hidden_action)
        
        view_menu.addSeparator()
        
        # View mode options
        view_mode_group = QActionGroup(self)
        
        list_view_action = QAction("As List", self)
        list_view_action.setCheckable(True)
        list_view_action.setChecked(self.view_mode == "list")
        list_view_action.triggered.connect(lambda: self._set_view_mode("list"))
        view_mode_group.addAction(list_view_action)
        view_menu.addAction(list_view_action)
        
        icons_view_action = QAction("As Icon and Text", self)
        icons_view_action.setCheckable(True)
        icons_view_action.setChecked(self.view_mode == "icons")
        icons_view_action.triggered.connect(lambda: self._set_view_mode("icons"))
        view_mode_group.addAction(icons_view_action)
        view_menu.addAction(icons_view_action)
        
        columns_view_action = QAction("As Columns", self)
        columns_view_action.setCheckable(True)
        columns_view_action.setChecked(self.view_mode == "columns")
        columns_view_action.triggered.connect(lambda: self._set_view_mode("columns"))
        view_mode_group.addAction(columns_view_action)
        view_menu.addAction(columns_view_action)
        
        gallery_view_action = QAction("As Gallery", self)
        gallery_view_action.setCheckable(True)
        gallery_view_action.setChecked(self.view_mode == "gallery")
        gallery_view_action.triggered.connect(lambda: self._set_view_mode("gallery"))
        view_mode_group.addAction(gallery_view_action)
        view_menu.addAction(gallery_view_action)
        
        view_menu.addSeparator()
        
        # Column submenu
        columns_menu = view_menu.addMenu("Add Columns")
        
        # Date modified column
        date_mod_action = QAction("Date Modified", self)
        date_mod_action.setCheckable(True)
        date_mod_action.setChecked("date_modified" in self.active_columns)
        date_mod_action.triggered.connect(lambda: self._toggle_column("date_modified", 3))
        columns_menu.addAction(date_mod_action)
        
        # Date created column
        date_created_action = QAction("Date Created", self)
        date_created_action.setCheckable(True)
        date_created_action.setChecked("date_created" in self.active_columns)
        date_created_action.triggered.connect(lambda: self._toggle_column("date_created", 4))
        columns_menu.addAction(date_created_action)
        
        # Type column
        type_action = QAction("Kind", self)
        type_action.setCheckable(True)
        type_action.setChecked("kind" in self.active_columns)
        type_action.triggered.connect(lambda: self._toggle_column("kind", 2))
        columns_menu.addAction(type_action)
        
        # Size column
        size_action = QAction("Size", self)
        size_action.setCheckable(True)
        size_action.setChecked("size" in self.active_columns)
        size_action.triggered.connect(lambda: self._toggle_column("size", 1))
        columns_menu.addAction(size_action)
        
        context_menu.exec(self.tree_view.header().mapToGlobal(pos))
        
    def _connect_signals(self):
        """Connect widget signals."""
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.path_edit.returnPressed.connect(self._on_path_changed)
        self.refresh_button.clicked.connect(self._refresh)
        self.nav_button.clicked.connect(self._go_up)  # Default action for nav button is go up
        
        # Set up hover tooltip for path edit
        self.path_edit.installEventFilter(self)
        
        # Path editor is already using eventFilter
        
        # Set up filter timer
        self.path_edit.textChanged.connect(self._on_path_text_changed)
        self.filter_timer.timeout.connect(self._apply_filter)
        
    def eventFilter(self, obj, event):
        """Event filter for hover tooltip.
        
        Args:
            obj: Object being filtered
            event: Event to filter
            
        Returns:
            True if event was handled, otherwise default handling
        """
        if obj == self.path_edit and event.type() == event.Type.ToolTip:
            # Show full path as tooltip
            item_count = self._get_directory_item_count()
            hidden_count = self._get_hidden_item_count() if self.show_hidden_files else 0
            tooltip = f"<b>{self.current_path}</b><br>{item_count} items"
            if hidden_count > 0:
                tooltip += f" ({hidden_count} hidden)"
            QToolTip.showText(event.globalPos(), tooltip)
            return True
        return super().eventFilter(obj, event)
        
    def _get_directory_item_count(self) -> int:
        """Get the number of items in the current directory.
        
        Returns:
            Number of items
        """
        dir_path = QDir(self.current_path)
        dir_path.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        return len(dir_path.entryList())
        
    def _get_hidden_item_count(self) -> int:
        """Get the number of hidden items in the current directory.
        
        Returns:
            Number of hidden items
        """
        dir_path = QDir(self.current_path)
        dir_path.setFilter(QDir.Filter.Hidden | QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        return len(dir_path.entryList())
        
    def _on_item_clicked(self, index):
        """Handle item click.
        
        Args:
            index: Model index of clicked item
        """
        file_path = self.file_model.filePath(index)
        self.file_selected.emit(file_path)
        
    def _on_item_double_clicked(self, index):
        """Handle item double click.
        
        Args:
            index: Model index of double-clicked item
        """
        file_path = self.file_model.filePath(index)
        
        if self.file_model.isDir(index):
            self.navigate_to(file_path)
        else:
            # TODO: Open file in editor
            print(f"Open file: {file_path}")
            
    def _on_path_changed(self):
        """Handle path edit change."""
        new_path = self.path_edit.text()
        
        # Check if this is a glob pattern
        if any(c in new_path for c in "*?[]"):
            self._apply_filter_pattern(new_path)
            return
            
        # Check if path exists
        if QDir(new_path).exists():
            self.navigate_to(new_path)
        elif os.path.exists(os.path.expanduser(new_path)):
            # Try expanding ~
            self.navigate_to(os.path.expanduser(new_path))
        elif os.path.exists(os.path.expandvars(new_path)):
            # Try expanding environment variables
            self.navigate_to(os.path.expandvars(new_path))
        else:
            # Reset to current path if invalid
            self.path_edit.setText(self.current_path)
            
    def _on_path_text_changed(self, text):
        """Handle path edit text changed.
        
        Args:
            text: New text in path edit
        """
        # If text contains glob patterns, start filter timer
        if any(c in text for c in "*?[]"):
            self.filter_timer.start()
            
    def _apply_filter(self):
        """Apply the current filter pattern."""
        pattern = self.path_edit.text()
        self._apply_filter_pattern(pattern)
            
    def _apply_filter_pattern(self, pattern):
        """Apply a glob filter pattern.
        
        Args:
            pattern: Glob pattern to filter by
        """
        if any(c in pattern for c in "*?[]"):
            self.path_filter = pattern
            # Set a name filter on the file model
            self.file_model.setNameFilters([pattern])
            self.file_model.setNameFilterDisables(False)  # Hide filtered items
        else:
            self.path_filter = ""
            self.file_model.setNameFilters([])
            # Reset the filter
            self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | 
                                     (QDir.Filter.Hidden if self.show_hidden_files else QDir.Filter.NoDotAndDotDot))
            
    def _refresh(self):
        """Refresh the current directory."""
        self.file_model.setRootPath("")  # Clear cache
        self.file_model.setRootPath(self.current_path)
        self.tree_view.setRootIndex(self.file_model.index(self.current_path))
        
        # Reapply any filters
        if self.path_filter:
            self._apply_filter_pattern(self.path_filter)
            
    def _go_up(self):
        """Go up one directory level."""
        parent_dir = QDir(self.current_path)
        if parent_dir.cdUp():
            self.navigate_to(parent_dir.absolutePath())
            
    def _go_back(self):
        """Navigate to the previous directory in history."""
        prev_path = self.navigation_history.go_back()
        if prev_path:
            self.set_root_path(prev_path, add_to_history=False)
            
        # Update navigation action states
        self.back_action.setEnabled(self.navigation_history.can_go_back())
        self.forward_action.setEnabled(self.navigation_history.can_go_forward())
            
    def _go_forward(self):
        """Navigate to the next directory in history."""
        next_path = self.navigation_history.go_forward()
        if next_path:
            self.set_root_path(next_path, add_to_history=False)
            
        # Update navigation action states
        self.back_action.setEnabled(self.navigation_history.can_go_back())
        self.forward_action.setEnabled(self.navigation_history.can_go_forward())
            
    def navigate_to(self, path: str):
        """Navigate to a specified path.
        
        Args:
            path: Path to navigate to
        """
        if QDir(path).exists() or QDir(os.path.expanduser(path)).exists():
            expanded_path = os.path.expanduser(path)
            self.set_root_path(expanded_path)
    
    def set_root_path(self, path: str, add_to_history: bool = True):
        """Set the root path for the file explorer.
        
        Args:
            path: Root directory path
            add_to_history: Whether to add this path to navigation history
        """
        if QDir(path).exists():
            self.current_path = path
            self.file_model.setRootPath(path)
            self.tree_view.setRootIndex(self.file_model.index(path))
            
            # Display basename in path editor for cleaner UI
            basename = os.path.basename(path) or path
            self.path_edit.setText(basename)
            # Set tooltip to show full path
            self.path_edit.setToolTip(path)
            
            # Apply hidden files setting
            self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | 
                                     (QDir.Filter.Hidden if self.show_hidden_files else QDir.Filter.NoDotAndDotDot))
            
            # Add to navigation history
            if add_to_history:
                self.navigation_history.add_path(path)
                self.back_action.setEnabled(self.navigation_history.can_go_back())
                self.forward_action.setEnabled(self.navigation_history.can_go_forward())
                
                # Save settings
                self._save_history()
                
            self.directory_changed.emit(path)
            
    def _copy_full_path(self):
        """Copy the full current path to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_path)
        
    def _copy_relative_path(self):
        """Copy the relative path to clipboard."""
        try:
            rel_path = os.path.relpath(self.current_path)
            clipboard = QApplication.clipboard()
            clipboard.setText(rel_path)
        except ValueError:
            # If paths are on different drives
            self._copy_full_path()
            
    def _paste_path(self):
        """Paste a path from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.path_edit.setText(text)
            self._on_path_changed()
            
    def _paste_env_vars(self):
        """Paste and expand environment variables."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            expanded_text = os.path.expandvars(text)
            self.path_edit.setText(expanded_text)
            self._on_path_changed()
            
    def _toggle_hidden_files(self, checked):
        """Toggle display of hidden files.
        
        Args:
            checked: Whether to show hidden files
        """
        self.show_hidden_files = bool(checked)
        if self.show_hidden_files:
            self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Hidden)
        else:
            self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        self._refresh()
        
        # Save setting
        self.settings.setValue("explorer/show_hidden", self.show_hidden_files)
        
    def _set_view_mode(self, mode):
        """Set the view mode.
        
        Args:
            mode: View mode (list, icons, columns, gallery)
        """
        self.view_mode = mode
        # Save setting
        self.settings.setValue("explorer/view_mode", self.view_mode)
        
        # Update tree view settings based on mode
        if mode == "list":
            # List view - compact with smaller icons
            self.tree_view.setIconSize(QSize(16, 16))
            self.tree_view.setRootIsDecorated(True)  # Show expand/collapse arrows
            self.tree_view.setIndentation(20)
            # Ensure name column is first and expanded
            self.tree_view.header().moveSection(0, 0)
            self.tree_view.header().resizeSection(0, 200)
            
        elif mode == "icons":
            # Icon view - larger icons
            self.tree_view.setIconSize(QSize(32, 32))
            self.tree_view.setRootIsDecorated(False)  # Hide expand/collapse arrows
            self.tree_view.setIndentation(10)
            # Expand name column
            self.tree_view.header().resizeSection(0, 250)
            
        elif mode == "columns":
            # Column view - emphasize all columns
            self.tree_view.setIconSize(QSize(16, 16))
            self.tree_view.setRootIsDecorated(False)
            self.tree_view.setIndentation(0)
            # Show all available columns
            for i in range(self.file_model.columnCount()):
                self.tree_view.header().showSection(i)
            # Make columns more visible
            self.tree_view.header().resizeSection(0, 180)  # Name
            self.tree_view.header().resizeSection(1, 80)   # Size
            self.tree_view.header().resizeSection(2, 80)   # Type
            self.tree_view.header().resizeSection(3, 120)  # Date Modified
            
        elif mode == "gallery":
            # Gallery view - maximize space for name/icon
            self.tree_view.setIconSize(QSize(48, 48))
            self.tree_view.setRootIsDecorated(False)
            self.tree_view.setIndentation(0)
            # Hide all columns except name
            for i in range(1, self.file_model.columnCount()):
                self.tree_view.header().hideSection(i)
            # Expand name column to fill view
            self.tree_view.header().resizeSection(0, self.tree_view.width() - 20)
            
        # Refresh model to update view
        current_index = self.tree_view.currentIndex()
        self.tree_view.setModel(None)
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(self.current_path))
        if current_index.isValid():
            self.tree_view.setCurrentIndex(current_index)
        
    def _toggle_column(self, column_id, column_index):
        """Toggle visibility of a column.
        
        Args:
            column_id: Column identifier
            column_index: Column index in the model
        """
        header = self.tree_view.header()
        
        if column_id in self.active_columns:
            # Remove column
            self.active_columns.remove(column_id)
            header.hideSection(column_index)
        else:
            # Add column
            self.active_columns.append(column_id)
            header.showSection(column_index)
            
        # Save setting
        self.settings.setValue("explorer/active_columns", self.active_columns)
            
        # Set appropriate width based on column type
        if column_id == "name":
            header.resizeSection(column_index, 200)
        elif column_id == "size":
            header.resizeSection(column_index, 80)
        elif column_id == "kind":
            header.resizeSection(column_index, 100)
        elif column_id == "date_modified":
            header.resizeSection(column_index, 120)
        elif column_id == "date_created":
            header.resizeSection(column_index, 120)
        else:
            header.resizeSection(column_index, 100)
                
    def _setup_sorting(self):
        """Set up column sorting functionality."""
        header = self.tree_view.header()
        
        # Enable sorting
        self.tree_view.setSortingEnabled(True)
        
        # Connect sort indicator changes
        header.sortIndicatorChanged.connect(self._on_sort_changed)
        
        # Default sort order (name, ascending)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def _on_sort_changed(self, column_index, sort_order):
        """Handle sort indicator changes.
        
        Args:
            column_index: Column index for sorting
            sort_order: Sort order (ascending/descending)
        """
        # Store current sort settings
        self.current_sort_column = column_index
        self.current_sort_order = sort_order
        
        # Save setting
        self.settings.setValue("explorer/sort_column", self.current_sort_column)
        
        # Update active sort menu items if needed
        for i, action in enumerate(self.sort_actions):
            action.setChecked(i == column_index)
                
        # Ensure the column is visible when sorting by it
        if column_index > 0 and self.tree_view.header().isSectionHidden(column_index):
            self.tree_view.header().showSection(column_index)
        
    def _set_sort_column(self, column_index):
        """Set the sort column.
        
        Args:
            column_index: Column index to sort by
        """
        # Ensure the column is visible
        if self.tree_view.header().isSectionHidden(column_index):
            # Find the corresponding column ID
            column_ids = {
                0: "name",
                1: "size",
                2: "kind",
                3: "date_modified",
                4: "date_created"
            }
            if column_index in column_ids:
                self._toggle_column(column_ids[column_index], column_index)
                
        # Sort
        self.tree_view.sortByColumn(column_index, self.current_sort_order)
        
    def _set_sort_order(self, order):
        """Set the sort order.
        
        Args:
            order: Sort order (ascending/descending)
        """
        self.current_sort_order = order
        self.tree_view.sortByColumn(self.current_sort_column, order)
        
    def _load_history(self):
        """Load navigation history from settings."""
        # Initialize empty history
        self.navigation_history = NavigationHistory()
        
        # Try to load history from settings
        if self.settings.contains("explorer/history"):
            history_list = self.settings.value("explorer/history")
            if isinstance(history_list, list):
                for path in history_list:
                    if path and os.path.exists(str(path)):
                        self.navigation_history.add_path(str(path))
            
        # If no valid history is loaded, add current path
        if not self.navigation_history.history:
            if os.path.exists(self.current_path):
                self.navigation_history.add_path(self.current_path)
            else:
                default_path = os.path.expanduser("~")
                self.current_path = default_path
                self.navigation_history.add_path(default_path)
        
        # Try to set current index from settings
        if self.settings.contains("explorer/history_index"):
            try:
                current_index = int(self.settings.value("explorer/history_index"))
                if 0 <= current_index < len(self.navigation_history.history):
                    self.navigation_history.current_index = current_index
            except (ValueError, TypeError):
                # If conversion fails, keep default index
                pass
            
    def _save_history(self):
        """Save navigation history to settings."""
        self.settings.setValue("explorer/history", self.navigation_history.history)
        self.settings.setValue("explorer/history_index", self.navigation_history.current_index)
        self.settings.setValue("explorer/current_path", self.current_path)
        self.settings.setValue("explorer/show_hidden", self.show_hidden_files)
        self.settings.setValue("explorer/view_mode", self.view_mode)
        self.settings.setValue("explorer/active_columns", self.active_columns)
        self.settings.setValue("explorer/sort_column", self.current_sort_column)
        self.settings.setValue("explorer/sort_order", self.current_sort_order == Qt.SortOrder.AscendingOrder)


class FileExplorerPanel(AbstractPanel):
    """File explorer panel for browsing files and directories."""
    
    def __init__(self, parent=None):
        """Initialize the file explorer panel."""
        super().__init__("File Explorer", parent)
        
        # Initialize all attributes in __init__
        self.explorer_widget = FileExplorerWidget()
        self.default_path = QDir.homePath()
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the file explorer panel UI."""
        self.setWidget(self.explorer_widget)
        
    def _connect_signals(self):
        """Connect explorer widget signals."""
        self.explorer_widget.directory_changed.connect(self._on_directory_changed)
        self.explorer_widget.file_selected.connect(self._on_file_selected)
        
    def _on_directory_changed(self, path):
        """Handle directory change.
        
        Args:
            path: New directory path
        """
        # Update window title or status bar with current directory
        self.setWindowTitle(f"File Explorer - {os.path.basename(path)}")
        
    def _on_file_selected(self, file_path):
        """Handle file selection.
        
        Args:
            file_path: Selected file path
        """
        # This could emit a signal to the main application
        # For now, we just print the selected file
        print(f"Selected file: {file_path}")
        
    def set_root_path(self, path: str):
        """Set the root path for the file explorer.
        
        Args:
            path: Root directory path
        """
        self.explorer_widget.set_root_path(path)
        
    def navigate_to_home(self):
        """Navigate to the user's home directory."""
        self.explorer_widget.navigate_to(os.path.expanduser("~"))
        
    def navigate_to_root(self):
        """Navigate to the root directory."""
        self.explorer_widget.navigate_to("/")
        
    def refresh(self):
        """Refresh the current directory view."""
        self.explorer_widget._refresh()
        
    def go_back(self):
        """Navigate to the previous directory in history."""
        self.explorer_widget._go_back()
        
    def go_forward(self):
        """Navigate to the next directory in history."""
        self.explorer_widget._go_forward()


class EnhancedFileExplorerPlugin(Plugin):
    """Enhanced File Explorer plugin implementation."""
    
    def __init__(self, name: str):
        """Initialize the plugin."""
        super().__init__(name, "2.0.0")
        
        # Initialize all attributes in __init__
        self.file_explorer_panel: Optional[FileExplorerPanel] = None
        self.default_path: str = QDir.homePath()
        
    def load(self) -> bool:
        """Load the file explorer plugin."""
        try:
            self.file_explorer_panel = FileExplorerPanel()
            if self.default_path:
                self.file_explorer_panel.set_root_path(self.default_path)
                
            print("Enhanced File Explorer plugin loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load Enhanced File Explorer plugin: {e}")
            return False
            
    def unload(self) -> bool:
        """Unload the file explorer plugin."""
        try:
            if self.file_explorer_panel:
                self.file_explorer_panel.close()
                self.file_explorer_panel = None
            print("Enhanced File Explorer plugin unloaded successfully")
            return True
        except Exception as e:
            print(f"Failed to unload Enhanced File Explorer plugin: {e}")
            return False
            
    def get_panels(self) -> List[AbstractPanel]:
        """Get panels provided by this plugin.
        
        Returns:
            List of panels provided by this plugin
        """
        return [self.file_explorer_panel] if self.file_explorer_panel else []
