from dataclasses import dataclass

from app.core.exceptions import ApplicationException


@dataclass(eq=False)
class AlreadyUserEmailException(ApplicationException):
    field: str

    @property
    def message(self):
        return f'Пользователь с таким email уже существую'

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class AlreadyUserUsernameException(ApplicationException):
    field: str

    @property
    def message(self):
        return f'Пользователь с таким username уже существую'

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class InvalidJWTTokenException(ApplicationException):
    @property
    def message(self):
        return 'Неправильный токен'

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class NotFoundUserByException(ApplicationException):
    text: str

    @property
    def message(self):
        return f"Пользователь с таким {self.text} не найдем"

    @property
    def status(self) -> int:
        return 404


@dataclass(eq=False)
class WrongDataException(ApplicationException):
    @property
    def message(self):
        return f"Неверные данные"

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class InvalidRoleNameException(ApplicationException):
    @property
    def message(self):
        return "Недопустимое имя роли. Должно быть от 3 до 24 символов."

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class SystemRoleAccessDeniedException(ApplicationException):
    @property
    def message(self):
        return "Доступ к системным ролям запрещен для обычных пользователей"

    @property
    def status(self) -> int:
        return 403


@dataclass(eq=False)
class ProtectedPermissionException(ApplicationException):
    @property
    def message(self):
        return "Доступ к защищенным правам запрещен"

    @property
    def status(self) -> int:
        return 403


@dataclass(eq=False)
class PermissionDeniedException(ApplicationException):
    @property
    def message(self):
        return "Отсутствует необходимое разрешение"

    @property
    def status(self) -> int:
        return 403


@dataclass(eq=False)
class InvalidSecurityLevelException(ApplicationException):
    @property
    def message(self):
        return "Уровень безопасности роли некорректен"

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class InsufficientSecurityLevelException(ApplicationException):
    @property
    def message(self):
        return "Недостаточный уровень безопасности для выполнения операции"

    @property
    def status(self) -> int:
        return 403


@dataclass(eq=False)
class NotFoundSessionException(ApplicationException):
    @property
    def message(self):
        return "Cессия не найдена"

    @property
    def status(self) -> int:
        return 404


@dataclass(eq=True)
class NotFoundRoleException(ApplicationException):
    role_name: str

    @property
    def message(self):
        return f"Роль {self.role_name} не найдена"

    @property
    def status(self) -> int:
        return 404


@dataclass(eq=True)
class NotFoundPermissionException(ApplicationException):
    permission_name: str

    @property
    def message(self):
        return f"Право {self.permission_name} не найдено"

    @property
    def status(self) -> int:
        return 404