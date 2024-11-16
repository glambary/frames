from datetime import date
from time import perf_counter_ns

from logs.config import logging_config
from logs.schemas import LogLevelsEnum
from services.start_limiter import SimpleStartLimiter


def main(excel_file_name: str, exe_file_name: str) -> None:
    """Главная функция."""
    # Отметка времени старта
    start_time = perf_counter_ns()

    # Настройки логирования
    logging_config(LogLevelsEnum.DEBUG)

    # Пробная версия по "дата". Задать перед make exe.
    # Закомментировать, если не нужно
    SimpleStartLimiter(date(2024, 11, 15))()

    # Получение данных из excel файла
    ...

    # Черчение обрамлений
    ...

    # Отметка времени окончания
    end_time = perf_counter_ns()
    t = end_time - start_time
    # Сообщение о выполнении / статистика


if __name__ == "__main__":
    main()
