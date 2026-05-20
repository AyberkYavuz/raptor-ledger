from fastapi import HTTPException


class HTTPExceptionWithCode(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        """Constructs a structured application domain exception payload."""
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code
        self.message = message


def raise_http_exception(status_code: int, error_code: str, message: str):
    """Factory helper to terminate runtime contexts with precise validation tracking."""
    raise HTTPExceptionWithCode(
        status_code=status_code,
        error_code=error_code,
        message=message
    )
