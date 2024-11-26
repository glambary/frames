class BaseCustomError(Exception):
    """Базовое исключение."""


class UnexpectedResultError(BaseCustomError):
    """Неожиданный результат."""


class StartUpError(BaseCustomError):
    """Ошибка при запуске."""


class InternalError(BaseCustomError):
    """Внутренняя ошибка."""


class ValueFromUserError(BaseCustomError):
    """Ошибка значения от пользователя."""
