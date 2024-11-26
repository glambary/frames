import logging
from time import perf_counter, sleep

from exception.custom import BaseCustomError, StartUpError, ValueFromUserError
from logs.config import logging_config
from logs.schemas import LogLevelsEnum
from services.excel.schemas.input import RangeCellInputSchema, SheetInputSchema
from services.excel.service import ExcelService
from services.frames.frames_one_fold import FramesOneFold
from services.frames.schemas.frames_common.input import FramesBaseInputSchema
from services.frames.schemas.frames_one_fold.input import (
    FramesOneFoldConstructionInputSchema,
    FramesOneFoldInputSchema,
    HolesInputSchema,
)


def main(excel_file_name: str, exe_file_name: str) -> None:
    """Главная функция."""
    # Настройки логирования
    logging_config(LogLevelsEnum.DEBUG)
    # Отключение loggers библиотек
    logging.getLogger("ezdxf").propagate = False

    # Пробная версия по "даты". Задать перед созданием exe файла!
    # Закомментировать, если не нужно
    # SimpleStartLimiter(date(2024, 11, 15))()

    # Получение данных из schemas файла
    excel_service = ExcelService("Обрамления.xlsx")
    sheet_params = SheetInputSchema(index=0)
    base_data = excel_service.get_cell_values(
        sheet_params=sheet_params,
        cells={
            "number_order": "J2",
            "date_order": "J3",
            "name_client": "J4",
            "address_order": "J5",
            "path_folder": "J6",
            "doorway": "J9",
            "thickness": "J10",
            "height_platband_stands": "J12",
        },
        raw_answer=False,
        validate_to_schema=FramesBaseInputSchema,
    )
    frames_data, frames_data_exc = excel_service.get_rows_data(
        sheet_params=sheet_params,
        range_cell_params=RangeCellInputSchema(
            start_row=2,
            end_row=52,
            start_column=1,
            end_column=7,
        ),
        raw_answer=False,
        columns={
            1: "number",
            2: "depth",
            3: "width_left",
            4: "width_right",
            5: "height_top",
            6: "button_hole_left",
            7: "button_hole_right",
        },
        validate_to_schema=FramesOneFoldInputSchema,
    )
    holes_data = excel_service.get_cell_values(
        sheet_params=sheet_params,
        cells={
            "diameter": "J14",
            "top": "J16",
            "bottom": "J17",
            "middle": "J18",
            "from_edge": "J19",
            "button_hole_x_center_coordinate": "J22",
            "button_hole_y_center_coordinate": "J23",
        },
        raw_answer=False,
        validate_to_schema=HolesInputSchema,
    )
    construction_data = excel_service.get_cell_values(
        sheet_params=sheet_params,
        cells={
            "thickness_frames": "J11",
        },
        raw_answer=False,
        validate_to_schema=FramesOneFoldConstructionInputSchema,
    )

    # Черчение обрамлений
    FramesOneFold(
        base_data=base_data,
        thickness_frames=construction_data.thickness_frames,
        holes_data=holes_data,
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
    except BaseCustomError as exc:
        logging.error("Произошла ошибка.", exc_info=exc)
    except Exception as exc:
        logging.critical("Незапланированная ошибка.", exc_info=exc)

    end_time = perf_counter()

    logging.info(f"Время выполнения t={end_time - start_time} сек.")

    sleep(120)
