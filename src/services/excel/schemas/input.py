from typing import Any

from pydantic import BaseModel, NonNegativeInt, PositiveInt, model_validator

from exception.custom import ValueFromUserError


class RangeCellInputSchema(BaseModel):
    """Схема диапазона ячеек для обхода schemas документа построчно."""

    start_row: PositiveInt
    end_row: PositiveInt
    start_column: PositiveInt
    end_column: PositiveInt


class SheetInputSchema(BaseModel):
    """Схема параметров для получения страницы schemas документа."""

    name: str | None = None
    index: NonNegativeInt | None = None

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Проверяет входные значения."""
        if data.get("name") is None and data.get("index") is None:
            raise ValueFromUserError(
                "Один из параметров name, index обязателен."
            )

        return data


class CellCoordinatesInputSchema(BaseModel):
    """Схема строки и колонки ячейки."""

    row: PositiveInt
    column: PositiveInt

    def __hash__(self):
        """Возвращает хэш."""
        return hash((self.row, self.column))
