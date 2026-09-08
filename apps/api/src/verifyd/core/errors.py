from typing import Any, Dict, Optional


class VerifydError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(VerifydError):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)


class PermissionDeniedError(VerifydError):
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="PERMISSION_DENIED", status_code=403, details=details)


class ValidationError(VerifydError):
    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=code, status_code=422, details=details)


class ConflictError(VerifydError):
    def __init__(self, message: str = "Conflict occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="CONFLICT", status_code=409, details=details)


class DomainStateError(VerifydError):
    def __init__(self, message: str = "Illegal state transition", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="ILLEGAL_STATE_TRANSITION", status_code=400, details=details)


class TransientAIError(VerifydError):
    def __init__(self, message: str = "Transient AI provider error, retrying", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="AI_TRANSIENT_ERROR", status_code=503, details=details)


class ProviderError(VerifydError):
    def __init__(self, message: str = "AI provider encountered an unrecoverable error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="AI_PROVIDER_ERROR", status_code=502, details=details)


class ClauseExtractionFailedError(VerifydError):
    def __init__(self, message: str = "Failed to extract checkable clauses from contract", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="CLAUSE_EXTRACTION_FAILED", status_code=422, details=details)
