from typing import Any

from pydantic import BaseModel


class PlatbandPostInternalSchema(BaseModel):
    """Внутренняя схема стойки обрамления."""

    depth: float
    width: float
    button_hole: str | None

    def __hash__(self) -> int:
        """Возвращает хэш."""
        return hash((self.depth, self.width, self.button_hole))

    def __eq__(self, other: Any) -> bool:
        """Возвращает результат сравнения объектов."""
        return all(
            (
                self.depth == other.depth,
                self.width == other.width,
                self.button_hole == other.button_hole,
            )
        )
