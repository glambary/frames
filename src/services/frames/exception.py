class FramesBaseError(Exception):
    """Базовое ошибка excel."""


class FramesValueFromUserError(FramesBaseError):
    """Ошибка значения от пользователя."""


class FramesNeverError(FramesBaseError):
    """Ошибка в коде."""
