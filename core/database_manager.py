"""
Database Manager - Handles database operations and schema management.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, List, Union

from PySide6.QtCore import QObject, Signal


class DatabaseManager(QObject):
    """Manages database operations for the PO Editor."""
    
    # Signals
    database_connected = Signal()
    database_disconnected = Signal()
    database_error = Signal(str)  # Error message
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the database file. If None, uses default location.
        """
        super().__init__()
        
        if db_path is None:
            # Default database location
            project_root = Path(__file__).parent.parent
            db_dir = project_root / "data"
            db_dir.mkdir(exist_ok=True)
            self.db_path = str(db_dir / "poeditor.db")
        else:
            self.db_path = db_path
            
        self.connection: Optional[sqlite3.Connection] = None
        
    def initialize(self) -> bool:
        """Initialize the database connection and create tables.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            self._create_tables()
            self.database_connected.emit()
            print(f"Database initialized at: {self.db_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            print(error_msg)
            self.database_error.emit(error_msg)
            return False
            
    def _create_tables(self):
        """Create the database tables."""
        if not self.connection:
            raise RuntimeError("Database connection not established")
        cursor = self.connection.cursor()
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Translation memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                target_text TEXT NOT NULL,
                source_lang TEXT NOT NULL,
                target_lang TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_text, target_text, source_lang, target_lang)
            )
        """)
        
        # Recent files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recent_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                entry_count INTEGER
            )
        """)
        
        # Plugin data table (for plugins to store their data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(plugin_name, key)
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)
        
        if not self.connection:
            raise RuntimeError("Database connection not established")
        self.connection.commit()
        
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.database_disconnected.emit()
            print("Database connection closed")
            
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows
        """
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
        
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        if not self.connection:
            raise RuntimeError("Database not connected")
            
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount
        
    # Settings methods
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            rows = self.execute_query(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            return rows[0]["value"] if rows else default
        except Exception as e:
            print(f"Error getting setting '{key}': {e}")
            return default
            
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.execute_update(
                """INSERT OR REPLACE INTO settings (key, value, updated_at) 
                   VALUES (?, ?, CURRENT_TIMESTAMP)""",
                (key, str(value))
            )
            return True
        except Exception as e:
            print(f"Error setting '{key}': {e}")
            return False
            
    # Translation memory methods
    def add_translation(self, source: str, target: str, source_lang: str, 
                       target_lang: str, context: Optional[str] = None) -> bool:
        """Add a translation to the translation memory.
        
        Args:
            source: Source text
            target: Target text
            source_lang: Source language code
            target_lang: Target language code
            context: Optional context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.execute_update(
                """INSERT OR REPLACE INTO translation_memory 
                   (source_text, target_text, source_lang, target_lang, context, updated_at)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (source, target, source_lang, target_lang, context)
            )
            return True
        except Exception as e:
            print(f"Error adding translation: {e}")
            return False
            
    def search_translations(self, query: str, source_lang: Optional[str] = None, 
                          target_lang: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search for translations in the translation memory.
        
        Args:
            query: Search query
            source_lang: Optional source language filter
            target_lang: Optional target language filter
            limit: Maximum number of results
            
        Returns:
            List of translation dictionaries
        """
        try:
            sql = """SELECT source_text, target_text, source_lang, target_lang, context
                     FROM translation_memory 
                     WHERE source_text LIKE ? OR target_text LIKE ?"""
            params = [f"%{query}%", f"%{query}%"]
            
            if source_lang:
                sql += " AND source_lang = ?"
                params.append(source_lang)
                
            if target_lang:
                sql += " AND target_lang = ?"
                params.append(target_lang)
                
            sql += " ORDER BY updated_at DESC LIMIT ?"
            params.append(str(limit))
            
            rows = self.execute_query(sql, tuple(params))
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error searching translations: {e}")
            return []
            
    # Recent files methods
    def add_recent_file(self, file_path: str, file_size: Optional[int] = None, 
                       entry_count: Optional[int] = None) -> bool:
        """Add a file to the recent files list.
        
        Args:
            file_path: Path to the file
            file_size: Optional file size
            entry_count: Optional entry count
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.execute_update(
                """INSERT OR REPLACE INTO recent_files 
                   (file_path, last_opened, file_size, entry_count)
                   VALUES (?, CURRENT_TIMESTAMP, ?, ?)""",
                (file_path, file_size, entry_count)
            )
            return True
        except Exception as e:
            print(f"Error adding recent file: {e}")
            return False
            
    def get_recent_files(self, limit: int = 10) -> List[Dict]:
        """Get recent files list.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of recent file dictionaries
        """
        try:
            rows = self.execute_query(
                """SELECT file_path, last_opened, file_size, entry_count
                   FROM recent_files 
                   ORDER BY last_opened DESC LIMIT ?""",
                (limit,)
            )
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting recent files: {e}")
            return []
            
    # Plugin data methods
    def set_plugin_data(self, plugin_name: str, key: str, value: Any) -> bool:
        """Set plugin-specific data.
        
        Args:
            plugin_name: Name of the plugin
            key: Data key
            value: Data value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.execute_update(
                """INSERT OR REPLACE INTO plugin_data 
                   (plugin_name, key, value, updated_at)
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                (plugin_name, key, str(value))
            )
            return True
        except Exception as e:
            print(f"Error setting plugin data: {e}")
            return False
            
    def get_plugin_data(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Get plugin-specific data.
        
        Args:
            plugin_name: Name of the plugin
            key: Data key
            default: Default value if not found
            
        Returns:
            Data value or default
        """
        try:
            rows = self.execute_query(
                "SELECT value FROM plugin_data WHERE plugin_name = ? AND key = ?",
                (plugin_name, key)
            )
            return rows[0]["value"] if rows else default
        except Exception as e:
            print(f"Error getting plugin data: {e}")
            return default
