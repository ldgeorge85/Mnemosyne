"""
Exceptions for the Tools & Plugin System
"""


class ToolException(Exception):
    """Base exception for all tool-related errors"""
    pass


class ToolNotFoundError(ToolException):
    """Raised when a requested tool is not found in the registry"""
    pass


class ToolExecutionError(ToolException):
    """Raised when a tool fails during execution"""
    pass


class ToolValidationError(ToolException):
    """Raised when tool input validation fails"""
    pass


class ToolTimeoutError(ToolException):
    """Raised when a tool execution times out"""
    pass


class ToolAuthenticationError(ToolException):
    """Raised when authentication is required but not provided"""
    pass


class ToolRateLimitError(ToolException):
    """Raised when a tool's rate limit is exceeded"""
    pass


class ToolConfigurationError(ToolException):
    """Raised when a tool is misconfigured"""
    pass