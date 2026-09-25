"""
Centralized application exceptions.

Using dedicated exception classes (instead of raising raw HTTPException
everywhere) keeps error semantics consistent and lets the FastAPI exception
handlers (registered in app/main.py) translate them into uniform JSON
error responses.
"""


class AppException(Exception):
    """Base class for all application-raised errors."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    def __init__(
        self, message: str = "You do not have permission to perform this action"
    ) -> None:
        super().__init__(message, status_code=403)


class ValidationError(AppException):
    def __init__(self, message: str = "Invalid input") -> None:
        super().__init__(message, status_code=422)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, status_code=409)


class UnsafeTargetError(AppException):
    """Raised when a scan is attempted against a target that is not
    explicitly marked as authorized in the database."""

    def __init__(
        self, message: str = "Target is not authorized for scanning"
    ) -> None:
        super().__init__(message, status_code=403)


class NmapExecutionError(AppException):
    def __init__(self, message: str = "Nmap execution failed") -> None:
        super().__init__(message, status_code=500)


class NmapParsingError(AppException):
    """Raised when Nmap XML output cannot be parsed into normalized data."""

    def __init__(self, message: str = "Failed to parse Nmap output") -> None:
        super().__init__(message, status_code=500)


class ScanInProgressError(AppException):
    def __init__(
        self, message: str = "A scan is already in progress for this target"
    ) -> None:
        super().__init__(message, status_code=409)


class ExternalDataUnavailableError(AppException):
    """Raised/used when vulnerability intelligence or other external data
    sources are unavailable. Callers must surface this transparently
    instead of fabricating data."""

    def __init__(
        self, message: str = "External data source is currently unavailable"
    ) -> None:
        super().__init__(message, status_code=503)