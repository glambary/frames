from enum import Enum, StrEnum


class ThicknessEnum(float, Enum):
    """Толщина материала."""

    ZERO_POINT_EIGHT = 0.8
    ONE_POINT_ZERO = 1.0
    ONE_POINT_TWO = 1.2


class SideEnum(StrEnum):
    """Сторона стойки."""

    LEFT = "лев"
    RIGHT = "прав"
    IDENTICAL = ""
