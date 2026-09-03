"""Domain-level exceptions, mapped to consistent HTTP error responses in app.main."""


class AppError(Exception):
    """Base class for all handled application errors."""

    code = "APPLICATION_ERROR"
    status_code = 400

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 400


class LifecycleError(AppError):
    """Raised when a requested state transition is not permitted by domain rules."""

    code = "LIFECYCLE_ERROR"
    status_code = 422
