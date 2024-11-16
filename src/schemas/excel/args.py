from typing import Any

from pydantic import (
    BaseModel,
    NonNegativeInt,
    NonPositiveInt,
    ValidationError,
    model_validator,
)


class RangeCellParamsSchema(BaseModel):
    """Схема диапазона ячеек для обхода excel документа построчно."""

    start_row: NonNegativeInt
    end_row: NonPositiveInt
    start_column: NonNegativeInt
    end_column: NonPositiveInt


class SheetParamsSchema(BaseModel):
    """Схема параметров для получения страницы excel документа."""

    name: str | None = None
    index: NonNegativeInt | None = None

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Проверяет входные значения."""
        if not (data["name"] or data["index"]):
            raise ValidationError("Один из параметров name, index обязателен.")

        return data


class CellCoordinatesSchema(BaseModel):
    """Схема строки и колонки ячейки."""

    row: NonNegativeInt
    column: NonNegativeInt
