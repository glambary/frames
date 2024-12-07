from collections.abc import Callable
from pathlib import Path
from typing import Any


class BaseService:
    """Базовый класс."""

    def _get_common_log_information(
        self, func: Callable[[Any, ...], Any]
    ) -> str:
        return f"{self.__class__.__name__}.{func.__name__}: "

    @staticmethod
    def _get_absolute_path(*path_parts: str) -> str:
        """
        Собирает абсолютный путь из нескольких частей и возвращает строку.

        :param path_parts: Части пути (каталоги, подкаталоги, файл).
        :return: Абсолютный путь.
        """
        return str(Path(*path_parts).resolve())
