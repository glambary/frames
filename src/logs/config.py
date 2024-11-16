import logging

from logs.schemas import LogLevelsEnum


def logging_config(log_level: LogLevelsEnum) -> None:
    """Задаёт config библиотеке logging."""
    logging.basicConfig(
        level=log_level,  # Уровень логирования
        format="%(asctime)s - %(levelname)s - %(message)s",  # формат логов
        handlers=[
            logging.FileHandler("app.log"),  # запись в файл
            logging.StreamHandler(),  # вывод в консоль
        ],
    )
