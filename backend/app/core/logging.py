"""
Logging Configuration

This module configures the application logging system, providing structured logging
capabilities with various output formats and severity levels.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Formats log records as JSON objects with consistent fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            A JSON-formatted string representation of the log record
        """
        log_object = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields from the record
        if hasattr(record, "props"):
            log_object.update(record.props)
            
        # Add any extra attributes passed via the extra parameter
        for key, value in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread", "threadName",
                "props"
            ]:
                log_object[key] = value
                
        return json.dumps(log_object)


class StructuredLogger(logging.Logger):
    """
    Extended logger class that supports structured logging with additional context.
    """
    
    def _log_with_context(
        self,
        level: int,
        msg: str,
        args: Any,
        exc_info: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a message with additional context data.
        
        Args:
            level: The logging level
            msg: The log message
            args: Arguments to apply to the message
            exc_info: Exception information
            extra: Extra fields to add to the log record
            stack_info: Whether to include stack info
            context: Additional contextual information to include
        """
        if context:
            extra = extra or {}
            extra.update(context)
        
        super().log(level, msg, args, exc_info, extra, stack_info)
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a debug message with optional context.
        
        Args:
            msg: The message to log
            *args: Formatting arguments
            **kwargs: Additional arguments including context
        """
        context = kwargs.pop("context", None)
        self._log_with_context(logging.DEBUG, msg, args, context=context, **kwargs)
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an info message with optional context.
        
        Args:
            msg: The message to log
            *args: Formatting arguments
            **kwargs: Additional arguments including context
        """
        context = kwargs.pop("context", None)
        self._log_with_context(logging.INFO, msg, args, context=context, **kwargs)
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a warning message with optional context.
        
        Args:
            msg: The message to log
            *args: Formatting arguments
            **kwargs: Additional arguments including context
        """
        context = kwargs.pop("context", None)
        self._log_with_context(logging.WARNING, msg, args, context=context, **kwargs)
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an error message with optional context.
        
        Args:
            msg: The message to log
            *args: Formatting arguments
            **kwargs: Additional arguments including context
        """
        context = kwargs.pop("context", None)
        self._log_with_context(logging.ERROR, msg, args, context=context, **kwargs)
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a critical message with optional context.
        
        Args:
            msg: The message to log
            *args: Formatting arguments
            **kwargs: Additional arguments including context
        """
        context = kwargs.pop("context", None)
        self._log_with_context(logging.CRITICAL, msg, args, context=context, **kwargs)


def configure_logging() -> None:
    """
    Configure the logging system for the application.
    Sets up handlers, formatters, and log levels based on application settings.
    """
    # Register the custom logger class
    logging.setLoggerClass(StructuredLogger)
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set the log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on settings
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging.getLogger(logger_name).setLevel(
            logging.INFO if settings.APP_ENV == "development" else logging.WARNING
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger, typically the module name
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
