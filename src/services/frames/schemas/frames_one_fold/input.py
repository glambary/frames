from typing import Any

from pydantic import BaseModel, Field, PositiveFloat


class FramesOneFoldInputSchema(BaseModel):
    number: Any
    depth: PositiveFloat
    width_left: PositiveFloat
    width_right: PositiveFloat
    height_top: PositiveFloat
    button_hole_left: str | None = Field(pattern=r"(\d{1,3})\*(\d{1,3})")
    button_hole_right: str | None = Field(pattern=r"(\d{1,3})\*(\d{1,3})")

    def __hash__(self) -> int:
        """
        Формирование хэша.

        Используется, для понимания какие верхние наличники одинаковые.
        """
        return hash(
            (self.depth, self.width_left, self.width_right, self.height_top)
        )


class HolesInputSchema(BaseModel):
    diameter: PositiveFloat | None
    top: PositiveFloat | None
    bottom: PositiveFloat | None
    middle: PositiveFloat | None
    from_edge: PositiveFloat | None

    button_hole_x_center_coordinate: PositiveFloat | None
    button_hole_y_center_coordinate: PositiveFloat | None


class FramesOneFoldConstructionInputSchema(BaseModel):
    thickness_frames: float
