# Sidebar Plugin Update

## Overview

Created a new core sidebar plugin that provides VS Code-like sidebar functionality with navigation buttons and content panels.

## Features Added

### SidebarButton

- Custom button class for sidebar navigation
- Active/inactive states with proper styling
- 50x50 pixel fixed size with hover effects
- Checkable buttons that stay pressed when active

### SidebarContentArea  

- Stacked widget container for panel content
- Manages multiple panels with show/hide functionality
- 250px fixed width content area

### SidebarPanel

- Main sidebar panel inheriting from AbstractPanel
- Horizontal layout with button strip (50px) and content area (250px)
- Toggle functionality - clicking active button hides sidebar
- Signal emission for panel state changes

### SidebarPlugin

- Core plugin implementation
- Automatic registration with plugin manager
- Default placeholder panels for Explorer and Search

## Integration Points

### MainFrame Changes

- Added sidebar_panel reference
- Special handling for sidebar panels in register_panel()
- Sidebar docked to left, other panels to right

### Plugin Manager

- Loads sidebar as core plugin
- Proper plugin lifecycle management

## File Structure

```
plugins/core/sidebar/
  plugin.py                 # Main plugin implementation
updates/sidebar/
  test_cases/               # Test files
  update_md/               # Documentation
    sidebar_update.md      # This file
```

## Design Principles

- All attributes initialized in __init__ methods
- No use of hasattr() or getattr()
- Direct attribute access only
- Proper type annotations with Optional[] for nullable types
- Clear separation of concerns between button, content, panel, and plugin classes

## Next Steps

- Integrate actual file explorer functionality
- Add search panel implementation  
- Create additional sidebar items (debug, extensions, etc.)
- Add icon support for buttons
- Implement panel persistence (remember last active panel)
