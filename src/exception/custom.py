class BaseCustomException(Exception):
    """Базовое исключение."""


class UnexpectedResultError(BaseCustomException):
    """Неожиданный результат."""


class StartUpError(BaseCustomException):
    """Ошибка при запуске."""


class InternalError(BaseCustomException):
    """Внутренняя ошибка."""


class ValueFromUserError(BaseCustomException):
    """Ошибка значения от пользователя."""
