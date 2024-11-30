class ExcelBaseError(Exception):
    """Базовое ошибка excel."""

    pass


class ExcelValueFromUserError(ExcelBaseError):
    """Ошибка значения от пользователя."""


class ExcelNeverError(ExcelBaseError):
    """Ошибка в коде."""
