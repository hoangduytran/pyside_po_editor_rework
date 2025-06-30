"""
Logging utilities for the PO Editor application
"""
import os
import logging
import logging.handlers
from typing import Dict, Any, Optional
from PySide6.QtCore import QSettings


class Logger:
    """Logger class that configures and provides logging functionality."""
    
    def __init__(self):
        """Initialize the logger."""
        self.logger = logging.getLogger('poeditor')
        self.logger.setLevel(logging.DEBUG)
        self.initialized = False
        self.settings = QSettings("POEditor", "Settings")
        
        # Initialize log handlers collection
        self.handlers = {}
        
        # Default configuration
        self.log_dir = os.path.join(os.path.expanduser('~'), '.poeditor', 'logs')
        self.max_file_size = 1024 * 1024  # 1MB default
        self.backup_count = 5
        self.log_level = logging.INFO
        self.console_logging = True
        self.file_logging = True
        
        # Load settings if available
        self.load_settings()
        
        # Create log directory if it doesn't exist
        if self.file_logging and not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        
    def load_settings(self):
        """Load logging settings from QSettings."""
        if self.settings.contains("logging/log_dir"):
            self.log_dir = self.settings.value("logging/log_dir")
            
        if self.settings.contains("logging/max_file_size"):
            try:
                self.max_file_size = int(self.settings.value("logging/max_file_size"))
            except (ValueError, TypeError):
                pass
                
        if self.settings.contains("logging/backup_count"):
            try:
                self.backup_count = int(self.settings.value("logging/backup_count"))
            except (ValueError, TypeError):
                pass
                
        if self.settings.contains("logging/log_level"):
            level_name = self.settings.value("logging/log_level")
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL
            }
            self.log_level = level_map.get(level_name, logging.INFO)
            
        if self.settings.contains("logging/console_logging"):
            self.console_logging = self.settings.value("logging/console_logging", type=bool)
            
        if self.settings.contains("logging/file_logging"):
            self.file_logging = self.settings.value("logging/file_logging", type=bool)
    
    def save_settings(self):
        """Save logging settings to QSettings."""
        self.settings.setValue("logging/log_dir", self.log_dir)
        self.settings.setValue("logging/max_file_size", self.max_file_size)
        self.settings.setValue("logging/backup_count", self.backup_count)
        
        # Map log level to string
        level_map = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL"
        }
        self.settings.setValue("logging/log_level", level_map.get(self.log_level, "INFO"))
        
        self.settings.setValue("logging/console_logging", self.console_logging)
        self.settings.setValue("logging/file_logging", self.file_logging)
        
    def setup(self):
        """Set up the logger with handlers based on settings."""
        if self.initialized:
            return
            
        # Set the logger level
        self.logger.setLevel(self.log_level)
        
        # Create console handler if enabled
        if self.console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.handlers['console'] = console_handler
        
        # Create file handler if enabled
        if self.file_logging:
            log_file = os.path.join(self.log_dir, 'poeditor.log')
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            file_handler.setLevel(self.log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.handlers['file'] = file_handler
            
        self.initialized = True
        
    def update_configuration(self, config: Dict[str, Any]):
        """Update logger configuration.
        
        Args:
            config: Dictionary with configuration parameters
        """
        # Update attributes from config
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        # Remove existing handlers
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            
        self.handlers = {}
        self.initialized = False
        
        # Save settings
        self.save_settings()
        
        # Re-setup logger with new configuration
        self.setup()
        
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance.
        
        Args:
            name: Optional name for the logger (used as sublogger of poeditor)
            
        Returns:
            Configured logger instance
        """
        if not self.initialized:
            self.setup()
            
        if name:
            return logging.getLogger(f'poeditor.{name}')
        return self.logger


# Create the global logger instance
lg = Logger()


# Convenience functions for accessing the logger
def debug(msg: str, *args, **kwargs):
    """Log a debug message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().debug(msg, *args, **kwargs)
    
def info(msg: str, *args, **kwargs):
    """Log an info message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().info(msg, *args, **kwargs)
    
def warning(msg: str, *args, **kwargs):
    """Log a warning message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().warning(msg, *args, **kwargs)
    
def error(msg: str, *args, **kwargs):
    """Log an error message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().error(msg, *args, **kwargs)
    
def critical(msg: str, *args, **kwargs):
    """Log a critical message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().critical(msg, *args, **kwargs)
    
def exception(msg: str, *args, **kwargs):
    """Log an exception message.
    
    Args:
        msg: Message to log
        args: Additional positional arguments
        kwargs: Additional keyword arguments
    """
    lg.get_logger().exception(msg, *args, **kwargs)
