import logging
from enum import IntEnum


class LogLevelsEnum(IntEnum):
    """Перечисление уровней логирования."""

    CRITICAL = logging.CRITICAL
    FATAL = CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET
