# PO Editor - Modern Gettext PO File Editor

A modern, plugin-based PO (Portable Object) file editor built with PySide6, designed for translators and localization professionals.

## Features

- **Plugin Architecture**: Extensible design with core and user plugins
- **Docking Panels**: Flexible UI with dockable/detachable panels
- **Database Support**: Built-in database for translation memory, settings, and plugin data
- **Modern UI**: Clean, responsive interface built with PySide6
- **Cross-platform**: Works on Windows, macOS, and Linux

## Architecture

### Core Components

- **MainFrame**: Main application window with docking support
- **AbstractPanel**: Base class for all dockable panels
- **PluginManager**: Handles plugin discovery, loading, and lifecycle
- **DatabaseManager**: Manages SQLite database operations

### Plugin System

The application supports two types of plugins:

1. **Core Plugins** (`plugins/core/`): Essential functionality
   - File Explorer
   - Search Panel
   - PO Table Editor
   - Database Browser

2. **User Plugins** (`plugins/user/`): Custom extensions
   - Custom translation tools
   - Third-party integrations
   - Specialized workflows

## Directory Structure

```
poeditor/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .vscode/               # VS Code configuration
│   └── settings.json
├── core/                  # Core application modules
│   ├── __init__.py
│   ├── main_frame.py      # Main window implementation
│   ├── abstract_panel.py  # Base panel class
│   ├── plugin_manager.py  # Plugin management
│   └── database_manager.py # Database operations
├── plugins/               # Plugin directory
│   ├── core/             # Core plugins
│   │   └── file_explorer/ # File browser plugin
│   │       └── plugin.py
│   └── user/             # User plugins
├── data/                 # Application data
│   └── poeditor.db      # SQLite database
└── docs/                # Documentation
```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd pyside_po_editor_rework
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

## Development

### Prerequisites

- Python 3.8+
- PySide6
- polib (for PO file handling)
- SQLAlchemy (for database operations)

### Creating Plugins

To create a new plugin:

1. Create a directory in `plugins/core/` or `plugins/user/`
2. Add a `plugin.py` file with your plugin class
3. Inherit from the `Plugin` base class
4. Implement required methods: `load()`, `unload()`, `get_panels()`

Example plugin structure:

```python
from core.plugin_manager import Plugin
from core.abstract_panel import AbstractPanel

class MyPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(name, "1.0.0")
        self.my_panel = None
        
    def load(self) -> bool:
        self.my_panel = MyPanel()
        return True
        
    def unload(self) -> bool:
        if self.my_panel:
            self.my_panel.close()
        return True
        
    def get_panels(self):
        return [self.my_panel] if self.my_panel else []
```

### Database API

Plugins can access the database through the `database_manager`:

```python
# Get plugin-specific data
value = self.database_manager.get_plugin_data("my_plugin", "setting_key")

# Store plugin data
self.database_manager.set_plugin_data("my_plugin", "setting_key", "value")

# Access translation memory
translations = self.database_manager.search_translations("hello")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[License information to be added]

## Roadmap

- [ ] PO file parsing and editing
- [ ] Translation memory integration
- [ ] Search and replace functionality
- [ ] Export/import features
- [ ] Plugin marketplace
- [ ] Collaborative translation features
- [ ] Integration with translation services

## Support

For support, please open an issue on the GitHub repository or contact the development team.
