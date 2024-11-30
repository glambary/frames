class BaseCustomError(Exception):
    """Базовое исключение."""


class UnexpectedResultError(BaseCustomError):
    """Неожиданный результат."""


class StartUpError(BaseCustomError):
    """Ошибка при запуске."""


class ValueFromUserError(BaseCustomError):
    """Ошибка значения от пользователя."""
