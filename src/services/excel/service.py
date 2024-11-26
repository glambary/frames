from typing import Any

from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

from exception.custom import UnexpectedResultError
from services.excel.schemas.input import (
    CellCoordinatesInputSchema,
    RangeCellInputSchema,
    SheetInputSchema,
)
from services.excel.types import BaseModelChildType


class ExcelService:
    """Сервис для взаимодействия с файлами schemas."""

    BaseReturnType = tuple[(tuple[Any, ...] | BaseModelChildType), ...]

    def __init__(self, file: str) -> None:
        self.workbook: Workbook = load_workbook(filename=file, data_only=True)

    def _get_sheet(self, sheet_params: SheetInputSchema) -> Worksheet:
        """Возвращает страницу документа."""
        sheet_name = sheet_params.name
        sheet_index = sheet_params.index

        if sheet_name is not None:
            return self.workbook[sheet_name]

        if sheet_index is not None:
            return self.workbook.worksheets[sheet_index]

        raise UnexpectedResultError("Недостижимый участок кода.")

    def get_rows_data(
        self,
        sheet_params: SheetInputSchema,
        range_cell_params: RangeCellInputSchema,
        raw_answer: bool = True,
        columns: dict[int, str] | None = None,
        validate_to_schema: type[BaseModelChildType] | None = None,
    ) -> (
        BaseReturnType
        | tuple[tuple[BaseReturnType, ...], dict[int, ValidationError]]
    ):
        """
        Возвращает информацию из schemas страницы построчно.

        :param sheet_params: Параметры для выбора страницы;
        :param range_cell_params: Параметры для выбора строк, столбцов;
        :param raw_answer: Вернуть сырой ответ или нет;
        :param columns: Если ответ НЕ сырой,
            то формат {номер_колонки: имя_поля из validate_to_schema}
        :param validate_to_schema: Pydantic схема;

        Если схема validate_to_schema не сможет создаться, то строка будет
        пропущена.
        """
        sheet: Worksheet = self._get_sheet(sheet_params)

        iter_rows = sheet.iter_rows(
            min_row=range_cell_params.start_row,
            max_row=range_cell_params.end_row,
            min_col=range_cell_params.start_column,
            max_col=range_cell_params.end_column,
            values_only=True,
        )

        if raw_answer:
            return tuple(iter_rows)

        for a in (columns, validate_to_schema):
            if not a:
                raise ValueError(
                    f"Для получения ответа в pydantic схемах, {a} обязателен."
                )

        result = []
        rows_with_exc = {}
        for n, row in enumerate(iter_rows, start=1):
            data = {
                field_name: row[column - 1]
                for column, field_name in columns.items()
            }

            # если ошибка валидации, то пропускаем строку
            try:
                result.append(validate_to_schema.model_validate(data))
            except ValidationError as exc:
                rows_with_exc[n] = exc
                # logging.warning(
                #     f"Значения строки {n} заполнены не полностью "
                #     f"или некорректно.",
                #     exc_info=exc,
                # )
                continue

        return tuple(result), rows_with_exc

    def get_cell_values(
        self,
        sheet_params: SheetInputSchema,
        cells: tuple[str | CellCoordinatesInputSchema, ...]
        | dict[str, str | CellCoordinatesInputSchema],
        raw_answer: bool = True,
        validate_to_schema: type[BaseModelChildType] | None = None,
    ) -> BaseReturnType:
        """
        Получает значения из указанных ячеек.

        1. Если `cells` передан в виде кортежа (tuple),
            возвращаются сырые данные (если `raw_answer=True`).
        2. Если `cells` передан в виде словаря (dict) и указана схема
            `validate_to_schema`, данные преобразуются и валидируются в объект
            Pydantic-схемы (если `raw_answer=False`).

        :param sheet_params: Параметры для выбора страницы.
        :param cells:
            - Кортеж адресов ячеек (например, "A1", "B2") или объектов
                `CellCoordinatesInputSchema` для получения сырых данных.
            - Словарь, где ключи - названия полей, а значения - адреса ячеек
                или объекты `CellCoordinatesInputSchema`, для валидации
                через Pydantic-схему.
        :param raw_answer:
            - Если True, возвращает сырые данные
                (только для `cells` в формате кортежа).
            - Если False, выполняет преобразование данных в Pydantic-схему
                (только для `cells` в формате словаря).
        :param validate_to_schema: Pydantic-схема для валидации данных,
            требуется, если `raw_answer=False`.

        :return: Сырые данные в виде кортежа или объект Pydantic-схемы.
        """

        def get_cell_value(cell: str | CellCoordinatesInputSchema) -> Any:
            if isinstance(cell, str):
                return sheet[cell].value
            if isinstance(cell, CellCoordinatesInputSchema):
                return sheet.cell(row=cell.row, column=cell.column).value

            raise TypeError(f"Некорректный тип ячейки: {type(cell).__name__}")

        sheet: Worksheet = self._get_sheet(sheet_params)

        if not cells:
            return ()

        # Проверка формата данных и флага raw_answer
        if isinstance(cells, tuple) and not raw_answer:
            raise ValueError(
                "Для `cells` в формате tuple `raw_answer` должен быть True."
            )
        if isinstance(cells, dict) and raw_answer:
            raise ValueError(
                "Для `cells` в формате dict `raw_answer` должен быть False."
            )

        # Обработка данных
        if isinstance(cells, tuple):
            # Сырые данные (только tuple)
            return tuple(get_cell_value(cell) for cell in cells)

        if isinstance(cells, dict):
            # Проверка наличия схемы для валидации
            if not validate_to_schema:
                raise ValueError(
                    "Для преобразования в Pydantic-схему необходимо "
                    "указать `validate_to_schema`."
                )
            # Преобразование данных для схемы
            data_to_validate = {
                field_name: get_cell_value(cell)
                for field_name, cell in cells.items()
            }
            return validate_to_schema.model_validate(data_to_validate)

        # Если формат cells не распознан
        raise ValueError(f"Некорректный формат cells: {type(cells).__name__}")
