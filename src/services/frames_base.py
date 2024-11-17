import math
from typing import assert_never

from ezdxf.math import ConstructionArc, Vec2

from schemas.frames_common.input import FramesBaseInputSchema
from services.ezdxf import EzDxfService


class FramesBase(EzDxfService):
    ZERO_POINT = Vec2(0, 0)

    def __init__(self, *, base_data: FramesBaseInputSchema) -> None:
        self.thickness = base_data.thickness
        self.height_platband_stands = base_data.height_platband_stands
        self.doorway = base_data.doorway

    @staticmethod
    def get_coordinates_angle_line(
        start_point: Vec2, angle_degrees: float, length: float
    ) -> Vec2:
        """
        Возвращает конечные координаты линии под углом.

        @param start_point: Стартовая точка;
        @param angle_degrees: Угол (по четвертям);
        @param length: Длина отрезка;
        @return: Vec2

        @raises: InternalError, если angle_degrees равен прямому углу
            (90, 180, 270, 360);
        """
        # приводим угол к диапазону от 0 до 360
        angle_degrees %= 360

        angle_degrees_radians = math.radians(angle_degrees)
        degrees_90_radians = math.radians(90)

        match angle_degrees:
            case x if 0 < x < 90:
                # 1 четверть
                angle_radians = degrees_90_radians - angle_degrees_radians
                delta_x = math.sin(angle_radians) * length
                delta_y = math.cos(angle_radians) * length
            case x if 90 < x < 180:
                # 2 четверть
                angle_radians = degrees_90_radians * 2 - angle_degrees_radians
                delta_x = -math.cos(angle_radians) * length
                delta_y = math.sin(angle_radians) * length
            case x if 180 < x < 270:
                # 3 четверть
                angle_radians = degrees_90_radians * 3 - angle_degrees_radians
                delta_x = -math.sin(angle_radians) * length
                delta_y = -math.cos(angle_radians) * length
            case x if 270 < x < 360:
                # 4 четверть
                angle_radians = degrees_90_radians * 4 - angle_degrees_radians
                delta_x = math.cos(angle_radians) * length
                delta_y = -math.sin(angle_radians) * length
            case x if x in (0, 90, 180, 270):
                raise ValueError(
                    "Метод get_coordinates_angle_line не предназначен для"
                    f"прямых углов (угол={x})."
                )
            case _ as unexpected:
                assert_never(unexpected)

        x_end = round(start_point.x + delta_x, 2)
        y_end = round(start_point.y + delta_y, 2)

        return Vec2(x_end, y_end)

    @staticmethod
    def get_drawing_arc_data(p1: Vec2, p2: Vec2, p3: Vec2, clockwise: bool):
        # Вычисляем центр и радиус окружности, проходящей через три точки
        arc = ConstructionArc.from_3p(p1, p3, p2, clockwise)

        center = arc.center
        radius = arc.radius

        start_angle = arc.start_angle
        end_angle = arc.end_angle

        return center, radius, start_angle, end_angle
