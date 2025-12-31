"""自訂例外類別"""


class AppException(Exception):
    """應用程式基礎例外"""

    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppException):
    """驗證錯誤"""

    def __init__(self, message: str):
        super().__init__("VALIDATION_ERROR", message, 400)


class AuthenticationError(AppException):
    """認證錯誤"""

    def __init__(self, message: str = "認證失敗"):
        super().__init__("AUTHENTICATION_ERROR", message, 401)


class AuthorizationError(AppException):
    """授權錯誤"""

    def __init__(self, message: str = "權限不足"):
        super().__init__("AUTHORIZATION_ERROR", message, 403)


class NotFoundError(AppException):
    """資源不存在"""

    def __init__(self, message: str = "資源不存在"):
        super().__init__("NOT_FOUND", message, 404)


class ExternalServiceError(AppException):
    """外部服務錯誤"""

    def __init__(self, service: str, message: str):
        super().__init__(
            f"{service.upper()}_ERROR",
            f"{service} 服務錯誤：{message}",
            502,
        )
