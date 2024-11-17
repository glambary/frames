import logging
from datetime import date
from time import perf_counter, perf_counter_ns, sleep

from exception.custom import (
    BaseCustomException,
    StartUpError,
    ValueFromUserError,
)
from logs.config import logging_config
from logs.schemas import LogLevelsEnum
from schemas.excel.input import SheetInputSchema
from schemas.frames_common.input import FramesBaseInputSchema
from services.excel import ExcelService
from services.frames_one_fold import FramesOneFold
from services.start_limiter import SimpleStartLimiter


def main(excel_file_name: str, exe_file_name: str) -> None:
    """Главная функция."""
    # Настройки логирования
    logging_config(LogLevelsEnum.DEBUG)
    # Отключение loggers библиотек
    logging.getLogger("ezdxf").propagate = False

    # Пробная версия по "даты". Задать перед созданием exe файла!
    # Закомментировать, если не нужно
    # SimpleStartLimiter(date(2024, 11, 15))()

    # Получение данных из excel файла
    excel_service = ExcelService("Обрамления.xlsx")
    base_data = excel_service.get_cell_values(
        sheet_params=SheetInputSchema(index=0),
        cells=("J2", "J3", "J4", "J5", "J6", "J10", "J11", "J12"),
        raw_answer=False,
        name_fields=(),
        validate_to_schema=FramesBaseInputSchema,
    )
    holes_data = ...
    frames_data = excel_service.get_rows_data(...)

    # Черчение обрамлений
    FramesOneFold(
        base_data=base_data,
        thickness_frames=...,
        holes_data=...,
    )(frames_data=frames_data)

    # Сообщение о выполнении / статистика


if __name__ == "__main__":
    start_time = perf_counter()

    try:
        main("1", "2")
    except ValueFromUserError as exc:
        logging.error(
            "Проверьте правильность введённых значений.", exc_info=exc
        )
    except StartUpError as exc:
        # если запущен SimpleStartLimiter
        logging.error("Пробный период окончен.", exc_info=exc)
    except BaseCustomException as exc:
        logging.error("Произошла ошибка.", exc_info=exc)
    except Exception as exc:
        logging.critical("Незапланированная ошибка.", exc_info=exc)

    end_time = perf_counter()

    logging.info(f"Время выполнения t={end_time - start_time} сек.")

    sleep(120)
