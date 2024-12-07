import logging
import os
import platform
from datetime import date, datetime
from typing import Literal

from exception.custom import StartUpError
from services.start_limiter.exception import StartLimiterError


class SimpleStartLimiter:
    """
    Ограничитель запуска приложения.

    Проверяет, чтобы дата в системе и BIOS была <= указанной дате (dt).
    Можно обмануть изменив время в системе и BIOS.

    :param dt: Дата включительно.

    :raises StartUpError: Если, текущее время больше, чем dt.
    """

    def __init__(self, dt: date | None = None) -> None:
        self.dt = dt

    def __call__(self):
        """Проверяет дату системы и BIOS."""
        if not self.dt:
            return

        system_date = datetime.now().date()
        bios_date = self._get_bios_date()

        if system_date > self.dt or bios_date > self.dt:
            raise StartLimiterError(f"Пробный период по {self.dt}.")

    @classmethod
    def _get_bios_date(cls) -> date:
        """Получает дату BIOS с использованием WMI."""
        if cls._get_system() == "Windows":
            import wmi
        else:
            return datetime.now().date()

        c = wmi.WMI()
        for bios in c.Win32_BIOS():
            release_date = bios.ReleaseDate  # Формат: YYYYMMDDHHMMSS.0+000
            if release_date:
                return datetime.strptime(release_date[:8], "%Y%m%d").date()

        raise StartUpError("Не удалось получить дату BIOS.")

    @staticmethod
    def _get_system() -> Literal["Linux", "Windows"] | None:
        """Проверяет, является ли система Windows."""
        if os.name == "posix" and platform.system() == "Linux":
            logging.debug("Распознана OS Linux.")
            return "Linux"
        if os.name == "nt" and platform.system() == "Windows":
            logging.debug("Распознана OS Windows.")
            return "Windows"

        return None
