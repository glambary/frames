import logging
from datetime import date
from sys import stdout
from time import perf_counter, sleep

from logs.config import logging_config
from logs.schemas import LogLevelsEnum
from services.excel.exceptions import ExcelNeverError, ExcelValueFromUserError
from services.excel.schemas.input import RangeCellInputSchema, SheetInputSchema
from services.excel.service import ExcelService
from services.frames.exception import FramesNeverError
from services.frames.frames_one_fold import FramesOneFold
from services.frames.schemas.frames_common.input import FramesBaseInputSchema
from services.frames.schemas.frames_one_fold.input import (
    FramesOneFoldConstructionInputSchema,
    FramesOneFoldInputSchema,
    HolesInputSchema,
)
from services.start_limiter.exception import StartLimiterError
from services.start_limiter.service import SimpleStartLimiter


def main(excel_file_name: str) -> None:
    """Главная функция."""
    column = "X"

    # Настройки логирования
    logging_config(LogLevelsEnum.DEBUG)
    # Отключение loggers библиотек
    logging.getLogger("ezdxf").propagate = False

    # Пробная версия по "даты". Задать перед созданием exe файла!
    # Закомментировать, если не нужно
    SimpleStartLimiter(date(2024, 12, 23))()

    # Получение данных из schemas файла
    excel_service = ExcelService(excel_file_name)
    sheet_params = SheetInputSchema(index=0)

    # открытие файла
    with excel_service:
        # Базовые данные
        base_data = excel_service.get_cell_values(
            sheet_params=sheet_params,
            cells={
                "number_order": f"{column}2",
                "date_order": f"{column}3",
                "name_client": f"{column}4",
                "address_order": f"{column}5",
                "path_folder": f"{column}6",
                "doorway": f"{column}9",
                "thickness": f"{column}10",
                "height_platband_stands": f"{column}12",
            },
            validate_to_schema=FramesBaseInputSchema,
        )

        # Данные по отверстиям под крепления, кнопки
        holes_data = excel_service.get_cell_values(
            sheet_params=sheet_params,
            cells={
                "diameter": f"{column}14",
                "top": f"{column}16",
                "bottom": f"{column}17",
                "middle": f"{column}18",
                "from_edge": f"{column}19",
                "button_hole_x_center_coordinate": f"{column}22",
                "button_hole_y_center_coordinate": f"{column}23",
            },
            validate_to_schema=HolesInputSchema,
        )

        # Данные по особенностям конструкции
        construction_data = excel_service.get_cell_values(
            sheet_params=sheet_params,
            cells={
                "thickness_frames": f"{column}11",
            },
            validate_to_schema=FramesOneFoldConstructionInputSchema,
        )

        # Данные по обрамлениям
        frames_data, frames_data_exc = excel_service.get_rows_data(
            sheet_params=sheet_params,
            range_cell_params=RangeCellInputSchema(
                start_row=3,
                end_row=353,
                start_column=1,
                end_column=7,
            ),
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

        need_identical = (
            True
            if excel_service.get_cell_values(
                sheet_params,
                cells=(f"{column}26",),
            )[0]
            == "+"
            else False
        )

    # Черчение обрамлений
    results, average_weight = FramesOneFold(
        base_data=base_data,
        thickness_frames=construction_data.thickness_frames,
        holes_data=holes_data,
    ).draw_frames(frames_data=frames_data, need_identical=need_identical)

    # Сообщение о выполнении / статистика
    if frames_data_exc:
        stdout.write("\n")
        stdout.write(
            f"Строки, в которых произошла ошибка: "
            f"{list(frames_data_exc.keys())}. "
            f"Количество - {len(frames_data_exc)}" + "\n"
        )
        stdout.write(str(frames_data_exc))
        stdout.write("\n")

    # Вывод результатов
    if results:
        stdout.write("\n")
        stdout.write("Информация по файлам:" + "\n")
        rows_all = set()
        for file_name, rows in results.items():
            stdout.write(f"{file_name} - {rows}." + "\n")
            rows_all.update(rows)

        stdout.write("\n")
        stdout.write(
            f"Количество начерченных комплектов обрамления - "
            f"{len(rows_all)}." + "\n"
        )

    # # средний вес
    # stdout.write("\n")
    # stdout.write(
    #     f"Средний вес комплекта: {round(average_weight, 2)} кг." + "\n"
    # )


if __name__ == "__main__":
    stdout.write("Старт программы." + "\n")
    stdout.write("\n")
    start_time = perf_counter()

    try:
        main("Обрамления.xlsx")
    except (ExcelNeverError, FramesNeverError) as exc:
        msg = "Произошла ошибка в коде. Сообщите разработчику."
        stdout.write(msg + "\n")
        logging.error(msg, exc_info=exc)
    except ExcelValueFromUserError as exc:
        msg = (
            "Пользовательская ошибка. Проверьте корректность введённых данных."
        )
        stdout.write(msg + "\n")
        logging.error(msg, exc_info=exc)
    except StartLimiterError as exc:
        # если запущен SimpleStartLimiter
        msg = "Внимание! Пробный период окончен."
        stdout.write(msg + "\n")
        logging.error(msg, exc_info=exc)
    except Exception as exc:
        msg = "Произошла незапланированная ошибка. Сообщите разработчику."
        stdout.write(msg + "\n")
        logging.critical(msg, exc_info=exc)

    end_time = perf_counter()

    stdout.write("\n")
    stdout.write(f"Время выполнения t={end_time - start_time} сек." + "\n")

    sleep(120)
