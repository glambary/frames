import math

from ezdxf.math import ConstructionArc, Vec2


class FramesBase:
    def __init__(self, dxf):
        self.dxf = dxf

    @staticmethod
    def get_coordinates_angle_line(
        start_point: Vec2, angle_degrees: float, length: float
    ) -> Vec2:
        # Приведем угол к диапазону от 0 до 360
        angle_degrees = angle_degrees % 360

        # Определим четверть
        if 0 <= angle_degrees < 90:
            # Первая четверть: x и y увеличиваются
            delta_x = length * math.cos(math.radians(angle_degrees))
            delta_y = length * math.sin(math.radians(angle_degrees))
        elif 90 <= angle_degrees < 180:
            # Вторая четверть: x уменьшается, y увеличивается
            delta_x = -length * math.sin(math.radians(180 - angle_degrees))
            delta_y = length * math.cos(math.radians(180 - angle_degrees))
        elif 180 <= angle_degrees < 270:
            # Третья четверть: x и y уменьшаются
            delta_x = -length * math.cos(math.radians(angle_degrees - 180))
            delta_y = -length * math.sin(math.radians(angle_degrees - 180))
        else:
            # Четвертая четверть: x увеличивается, y уменьшается
            delta_x = length * math.sin(math.radians(360 - angle_degrees))
            delta_y = -length * math.cos(math.radians(360 - angle_degrees))

        # Определяем конечные координаты
        x_end = round(start_point[0] + delta_x, 1)
        y_end = round(start_point[1] + delta_y, 1)

        return Vec2(x_end, y_end)

    @staticmethod
    def get_drawing_arc_data(p1: Vec2, p2: Vec2, p3: Vec2):
        # Вычисляем центр и радиус окружности, проходящей через три точки
        arc = ConstructionArc.from_3p(p1, p3, p2, False)

        center = arc.center
        radius = arc.radius

        start_angle = arc.start_angle
        end_angle = arc.end_angle

        return center, radius, start_angle, end_angle
