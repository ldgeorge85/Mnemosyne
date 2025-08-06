"""
Logging Configuration

This module configures the application logging system, providing structured logging
capabilities with various output formats and severity levels.
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
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
        
        # For f-strings (which are already formatted) or messages without formatting placeholders,
        # we don't need args for string formatting
        # Ensure we pass keyword arguments correctly to avoid misplacement that
        # leads to logging format errors (TypeError: not all arguments converted)
        kwargs_for_log = {
            "exc_info": exc_info,
            "extra": extra,
            "stack_info": stack_info,
        }

        if not args:
            # Call without positional args to avoid creating an args tuple that
            # breaks string formatting inside logging
            super().log(level, msg, **kwargs_for_log)
        else:
            super().log(level, msg, *args, **kwargs_for_log)
    
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
    
    # Create formatters
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler with rotation if not in development
    if settings.APP_ENV != "development":
        # Create logs directory if it doesn't exist
        log_dir = Path("/app/logs") if os.path.exists("/app") else Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Application logs
        app_log_file = log_dir / "app.log"
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Error logs (separate file for ERROR and above)
        error_log_file = log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    # Access logger (for HTTP requests)
    access_logger = logging.getLogger("uvicorn.access")
    if settings.LOG_FORMAT.lower() == "json":
        access_formatter = JsonFormatter()
    else:
        access_formatter = logging.Formatter(
            '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Clear existing handlers from access logger
    for handler in access_logger.handlers[:]:
        access_logger.removeHandler(handler)
    
    # Add console handler to access logger
    access_console_handler = logging.StreamHandler(sys.stdout)
    access_console_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_console_handler)
    access_logger.propagate = False
    
    # Reduce noise from third-party libraries
    for logger_name in ["uvicorn", "uvicorn.error"]:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.setLevel(
            logging.INFO if settings.APP_ENV == "development" else logging.WARNING
        )
    
    # Set SQL logging based on environment
    if settings.APP_ENV == "development":
        # Show SQL queries in development
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        # Hide SQL queries in production
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Configure httpx logging (used by OpenAI client)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger, typically the module name
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)


class LoggingContextFilter(logging.Filter):
    """
    A logging filter that adds contextual information to log records.
    This can include request IDs, user IDs, or other correlation data.
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the filter with context data.
        
        Args:
            context: Dictionary of contextual data to add to log records
        """
        super().__init__()
        self.context = context
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context data to the log record.
        
        Args:
            record: The log record to enhance
            
        Returns:
            True to allow the record to be logged
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def add_logging_context(logger: logging.Logger, context: Dict[str, Any]) -> None:
    """
    Add contextual information to a logger that will be included in all log messages.
    
    Args:
        logger: The logger to add context to
        context: Dictionary of contextual data
    """
    # Remove any existing context filters
    logger.filters = [f for f in logger.filters if not isinstance(f, LoggingContextFilter)]
    
    # Add new context filter
    logger.addFilter(LoggingContextFilter(context))
