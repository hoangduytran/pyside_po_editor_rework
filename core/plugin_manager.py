"""
Plugin Manager - Handles plugin discovery, loading, and lifecycle management.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QObject, Signal

from .abstract_panel import AbstractPanel


class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize the plugin.
        
        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.enabled = False
        self.main_window = None
        self.database_manager = None
        
    def initialize(self, main_window, database_manager):
        """Initialize the plugin with main window and database access.
        
        Args:
            main_window: Reference to the main window
            database_manager: Reference to the database manager
        """
        self.main_window = main_window
        self.database_manager = database_manager
        
    def load(self) -> bool:
        """Load the plugin. Override in subclasses.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        self.enabled = True
        return True
        
    def unload(self) -> bool:
        """Unload the plugin. Override in subclasses.
        
        Returns:
            True if unloaded successfully, False otherwise
        """
        self.enabled = False
        return True
        
    def get_panels(self) -> List[AbstractPanel]:
        """Get panels provided by this plugin.
        
        Returns:
            List of panel instances
        """
        return []
        
    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Get menu items provided by this plugin.
        
        Returns:
            List of menu item dictionaries
        """
        return []


class PluginManager(QObject):
    """Manages plugin discovery, loading, and lifecycle."""
    
    # Signals
    plugin_loaded = Signal(str)  # Plugin name
    plugin_unloaded = Signal(str)  # Plugin name
    plugin_error = Signal(str, str)  # Plugin name, error message
    
    def __init__(self):
        """Initialize the plugin manager."""
        super().__init__()
        
        self.main_window = None
        self.database_manager = None
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_directories = []
        
        # Set up plugin directories
        self._setup_plugin_directories()
        
    def _setup_plugin_directories(self):
        """Set up plugin directories."""
        project_root = Path(__file__).parent.parent
        
        # Core plugins directory
        core_plugins_dir = project_root / "plugins" / "core"
        if core_plugins_dir.exists():
            self.plugin_directories.append(str(core_plugins_dir))
            
        # User plugins directory
        user_plugins_dir = project_root / "plugins" / "user"
        if user_plugins_dir.exists():
            self.plugin_directories.append(str(user_plugins_dir))
            
    def set_main_window(self, main_window):
        """Set the main window reference.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        
    def set_database_manager(self, database_manager):
        """Set the database manager reference.
        
        Args:
            database_manager: Reference to the database manager
        """
        self.database_manager = database_manager
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins.
        
        Returns:
            List of plugin directory paths
        """
        plugin_paths = []
        
        for plugin_dir in self.plugin_directories:
            if not os.path.exists(plugin_dir):
                continue
                
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                if os.path.isdir(item_path):
                    # Check if it's a valid plugin directory
                    plugin_file = os.path.join(item_path, "plugin.py")
                    init_file = os.path.join(item_path, "__init__.py")
                    
                    if os.path.exists(plugin_file) or os.path.exists(init_file):
                        plugin_paths.append(item_path)
                        
        return plugin_paths
        
    def load_plugin(self, plugin_path: str) -> bool:
        """Load a plugin from the given path.
        
        Args:
            plugin_path: Path to the plugin directory
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            plugin_name = os.path.basename(plugin_path)
            
            # Add plugin path to sys.path temporarily
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
                
            # Try to import the plugin
            plugin_module = None
            
            # First try plugin.py
            plugin_file = os.path.join(plugin_path, "plugin.py")
            if os.path.exists(plugin_file):
                spec = importlib.util.spec_from_file_location(
                    f"{plugin_name}_plugin", plugin_file
                )
                if spec is None or spec.loader is None:
                    raise ImportError(f"Failed to create module spec for {plugin_name}")
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
            else:
                # Try importing as a package
                plugin_module = importlib.import_module(plugin_name)
                
            # Look for plugin class
            plugin_class = None
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    plugin_class = attr
                    break
                    
            if not plugin_class:
                raise ImportError(f"No plugin class found in {plugin_name}")
                
            # Create plugin instance
            plugin_instance = plugin_class(plugin_name)
            plugin_instance.initialize(self.main_window, self.database_manager)
            
            # Load the plugin
            if plugin_instance.load():
                self.plugins[plugin_name] = plugin_instance
                
                # Register plugin panels
                if self.main_window:
                    panels = plugin_instance.get_panels()
                    for panel in panels:
                        panel_id = f"{plugin_name}_{panel.__class__.__name__}"
                        panel.set_panel_id(panel_id)
                        self.main_window.register_panel(panel_id, panel)
                    
                self.plugin_loaded.emit(plugin_name)
                print(f"Plugin '{plugin_name}' loaded successfully")
                return True
            else:
                self.plugin_error.emit(plugin_name, "Plugin load() method returned False")
                return False
                
        except Exception as e:
            error_msg = f"Failed to load plugin from {plugin_path}: {str(e)}"
            print(error_msg)
            self.plugin_error.emit(os.path.basename(plugin_path), error_msg)
            return False
            
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            return False
            
        try:
            plugin = self.plugins[plugin_name]
            
            # Unregister plugin panels
            if self.main_window:
                panels = plugin.get_panels()
                for panel in panels:
                    panel_id = f"{plugin_name}_{panel.__class__.__name__}"
                    self.main_window.unregister_panel(panel_id)
                
            # Unload the plugin
            if plugin.unload():
                del self.plugins[plugin_name]
                self.plugin_unloaded.emit(plugin_name)
                print(f"Plugin '{plugin_name}' unloaded successfully")
                return True
            else:
                self.plugin_error.emit(plugin_name, "Plugin unload() method returned False")
                return False
                
        except Exception as e:
            error_msg = f"Failed to unload plugin '{plugin_name}': {str(e)}"
            print(error_msg)
            self.plugin_error.emit(plugin_name, error_msg)
            return False
            
    def discover_and_load_plugins(self):
        """Discover and load all available plugins."""
        plugin_paths = self.discover_plugins()
        
        # Load core plugins first
        core_plugins = [p for p in plugin_paths if "plugins/core" in p]
        user_plugins = [p for p in plugin_paths if "plugins/user" in p]
        
        for plugin_path in core_plugins + user_plugins:
            self.load_plugin(plugin_path)
            
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)
        
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())
        
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if loaded, False otherwise
        """
        return plugin_name in self.plugins
