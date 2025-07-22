# from app.core.api.exceptions import ProjectBaseException



# class AuthException(ProjectBaseException):
#     """
#     Ошибка аутентификации/авторизации в модуле auth.
#     По умолчанию статус-код 401, если не указано другое.
#     """
#     def __init__(self, message: str, http_status: int = 401):
#         super().__init__(message, http_status)


# class InvalidTokenException(ProjectBaseException):
#     """
#     Ошибка недействительного токена; по умолчанию - 401.
#     """
#     def __init__(self, message: str = "Token is invalid or expired"):
#         super().__init__(message, http_status=401)


# class UserNotFoundException(ProjectBaseException):
#     """
#     Ошибка "пользователь не найден".
#     """
#     def __init__(self, message: str = "User not found"):
#         super().__init__(message, http_status=404)
