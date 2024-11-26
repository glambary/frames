from collections import defaultdict
from collections.abc import Callable
from typing import Any, assert_never, cast

from ezdxf.math import Vec2

from exception.custom import ValueFromUserError
from services.frames.frames_base import FramesBase
from services.frames.schemas.frames_common.enums import SideEnum, ThicknessEnum
from services.frames.schemas.frames_one_fold.input import (
    FramesOneFoldInputSchema,
    HolesInputSchema,
)
from services.frames.schemas.frames_one_fold.internal import (
    PlatbandPostInternalSchema,
)


class FramesOneFold(FramesBase):
    SUPPORTED_THICKNESS = {ThicknessEnum.ONE_POINT_ZERO}
    # погрешность развёртки стали
    INACCURACY_STEEL_REAMER = {ThicknessEnum.ONE_POINT_ZERO: 3.63}

    def __init__(
        self,
        *,
        thickness_frames: float,
        holes_data: HolesInputSchema,
        **kwargs: dict[str, Any],
    ):
        super().__init__(**kwargs)

        self.thickness_frames = thickness_frames
        self.holes_data = holes_data

        # self.thickness из FramesBase
        if self.thickness not in self.SUPPORTED_THICKNESS:
            raise ValueFromUserError(
                f"Толщина {self.thickness} не поддерживается."
            )

        self._inaccuracy_steel_reamer = self.INACCURACY_STEEL_REAMER[
            self.thickness
        ]

    def __call__(
        self,
        frames_data: tuple[FramesOneFoldInputSchema, ...],
        # need_to_grouped: False,
    ):
        left_platbands: dict[PlatbandPostInternalSchema, list[str]] = (
            defaultdict(list)
        )
        right_platbands: dict[PlatbandPostInternalSchema, list[str]] = (
            defaultdict(list)
        )
        top_platbands: dict[FramesOneFoldInputSchema, list[str]] = defaultdict(
            list
        )

        for f in frames_data:
            # потому что в листе замеров без учета отгиба
            f.depth += self.thickness_frames

            left_schema = PlatbandPostInternalSchema(
                depth=f.depth,
                width=f.width_left,
                button_hole=f.button_hole_left,
            )
            right_schema = PlatbandPostInternalSchema(
                depth=f.depth,
                width=f.width_right,
                button_hole=f.button_hole_right,
            )
            number = f.number
            left_platbands[left_schema].append(number)
            right_platbands[right_schema].append(number)
            top_platbands[f].append(number)

        for data, numbers in left_platbands.items():
            self.draw_left_platband(data, numbers)

        for data, numbers in right_platbands.items():
            self.draw_right_platband(data, numbers)

        for data, numbers in top_platbands.items():
            self.draw_top_platband(data, numbers)

    def draw_left_platband(
        self, data: PlatbandPostInternalSchema, numbers: list[str]
    ) -> None:
        return self._draw_stand_platband(
            data=data, numbers=numbers, side=SideEnum.LEFT
        )

    def draw_right_platband(
        self, data: PlatbandPostInternalSchema, numbers: list[str]
    ) -> None:
        return self._draw_stand_platband(
            data=data, numbers=numbers, side=SideEnum.RIGHT
        )

    def draw_top_platband(
        self, data: FramesOneFoldInputSchema, numbers: list[str]
    ) -> None:
        document, model_space = self.get_document_and_model_space()

        inaccuracy_one_fold = 2.4
        inaccuracy_width = 1.354

        extension_length = 10
        thickness_frames_length = self.thickness_frames - inaccuracy_one_fold
        item_arc_length = 0.56
        pre_arc_length = 2.69
        height_length = data.height_top - 2.71

        # проём
        p1_left = Vec2(self.ZERO_POINT.x - self.doorway / 2, self.ZERO_POINT.y)
        p1_right = Vec2(
            self.ZERO_POINT.x + self.doorway / 2, self.ZERO_POINT.y
        )
        model_space.add_line(p1_left, p1_right)

        # Y - вырез под проём
        p2_y = p1_left.y + 60
        p2_left = Vec2(p1_left.x, p2_y)
        p2_right = Vec2(p1_right.x, p2_y)
        model_space.add_line(p1_left, p2_left)
        model_space.add_line(p1_right, p2_right)

        # X - расширение
        p3_left = Vec2(p2_left.x - extension_length, p2_left.y)
        p3_right = Vec2(p2_right.x + extension_length, p2_left.y)
        model_space.add_line(p2_left, p3_left)
        model_space.add_line(p2_right, p3_right)

        # Y - глубина
        p4_y = data.depth - thickness_frames_length - 60 - inaccuracy_one_fold
        p4_left = Vec2(p3_left.x, p3_left.y + p4_y)
        p4_right = Vec2(p3_right.x, p3_right.y + p4_y)
        model_space.add_line(p3_left, p4_left)
        model_space.add_line(p3_right, p4_right)

        # X - ширина под стойки
        p5_left = Vec2(
            p4_left.x
            - (data.width_right - inaccuracy_width - extension_length),
            p4_left.y,
        )
        p5_right = Vec2(
            p4_right.x
            + (data.width_left - inaccuracy_width - extension_length),
            p4_right.y,
        )
        model_space.add_line(p4_left, p5_left)
        model_space.add_line(p4_right, p5_right)

        # Y - отгиб толщина обрамления
        p6_y = p5_left.y + thickness_frames_length
        p6_left = Vec2(p5_left.x, p6_y)
        p6_right = Vec2(p5_right.x, p6_y)
        model_space.add_line(p5_left, p6_left)
        model_space.add_line(p5_right, p6_right)

        # первый вырез для гибки
        p7_left = self.get_coordinates_angle_line(p6_left, 65, pre_arc_length)
        p7_right = self.get_coordinates_angle_line(
            p6_right, 115, pre_arc_length
        )
        model_space.add_line(p6_left, p7_left)
        model_space.add_line(p6_right, p7_right)

        a1_left = p7_left
        a1_right = p7_right
        a2_left = self.get_coordinates_angle_line(
            a1_left, 100, item_arc_length
        )
        a2_right = self.get_coordinates_angle_line(
            a1_right, 80, item_arc_length
        )
        a3_left = self.get_coordinates_angle_line(
            a2_left, 170, item_arc_length
        )
        a3_right = self.get_coordinates_angle_line(
            a2_right, 10, item_arc_length
        )
        arc_data_1_left = self.get_drawing_arc_data(
            a1_left, a2_left, a3_left, clockwise=True
        )
        arc_data_1_right = self.get_drawing_arc_data(
            a1_right, a2_right, a3_right, clockwise=False
        )
        model_space.add_arc(*arc_data_1_left)
        model_space.add_arc(*arc_data_1_right)

        p8_left = a3_left
        p8_right = a3_right
        p9_left = self.get_coordinates_angle_line(
            p8_left, 180 + 25, pre_arc_length
        )
        p9_right = self.get_coordinates_angle_line(
            p8_right, 335, pre_arc_length
        )
        model_space.add_line(p8_left, p9_left)
        model_space.add_line(p8_right, p9_right)
        # первый вырез для гибки - конец

        # X - отгиб толщина обрамления
        p10_left = Vec2(p9_left.x - thickness_frames_length, p9_left.y)
        p10_right = Vec2(p9_right.x + thickness_frames_length, p9_right.y)
        model_space.add_line(p9_left, p10_left)
        model_space.add_line(p9_right, p10_right)

        # Y - высота наличника
        p11_left = Vec2(p10_left.x, p10_left.y + height_length)
        p11_right = Vec2(p10_right.x, p10_right.y + height_length)
        model_space.add_line(p10_left, p11_left)
        model_space.add_line(p10_right, p11_right)

        # X - отгиб толщина обрамления
        p12_left = Vec2(p11_left.x + thickness_frames_length, p11_left.y)
        p12_right = Vec2(p11_right.x - thickness_frames_length, p11_right.y)
        model_space.add_line(p11_left, p12_left)
        model_space.add_line(p11_right, p12_right)

        # второй вырез для гибки
        p13_left = self.get_coordinates_angle_line(
            p12_left, 270 + 65, pre_arc_length
        )
        p13_right = self.get_coordinates_angle_line(
            p12_right, 90 + 115, pre_arc_length
        )
        model_space.add_line(p12_left, p13_left)
        model_space.add_line(p12_right, p13_right)

        a4_left = p13_left
        a4_right = p13_right
        a5_left = self.get_coordinates_angle_line(
            a4_left, 270 + 100, item_arc_length
        )
        a5_right = self.get_coordinates_angle_line(
            a4_right, 90 + 80, item_arc_length
        )
        a6_left = self.get_coordinates_angle_line(
            a5_left, 270 + 170, item_arc_length
        )
        a6_right = self.get_coordinates_angle_line(
            a5_right, 90 + 10, item_arc_length
        )
        arc_data_2_left = self.get_drawing_arc_data(
            a4_left, a5_left, a6_left, clockwise=True
        )
        arc_data_2_right = self.get_drawing_arc_data(
            a4_right, a5_right, a6_right, clockwise=False
        )
        model_space.add_arc(*arc_data_2_left)
        model_space.add_arc(*arc_data_2_right)

        p14_left = a6_left
        p14_right = a6_right
        p15_left = self.get_coordinates_angle_line(
            p14_left, 90 + 25, pre_arc_length
        )
        p15_right = self.get_coordinates_angle_line(
            p14_right, 65, pre_arc_length
        )
        model_space.add_line(p14_left, p15_left)
        model_space.add_line(p14_right, p15_right)
        # второй вырез для гибки - конец

        # Y - отгиб толщина обрамления
        p16_y = p15_left.y + thickness_frames_length
        p16_left = Vec2(p15_left.x, p16_y)
        p16_right = Vec2(p15_right.x, p16_y)
        model_space.add_line(p15_left, p16_left)
        model_space.add_line(p15_right, p16_right)

        # замыкаю контур
        model_space.add_line(p16_left, p16_right)

        # отверстие под крепления
        if self.holes_data.diameter:
            h_delta = self.holes_data.from_edge - 0.42
            h_left = Vec2(p12_left.x + h_delta, p15_left.y - h_delta)
            h_right = Vec2(p12_right.x - h_delta, p15_right.y - h_delta)
            for h in (h_left, h_right):
                model_space.add_circle(
                    center=h, radius=self.holes_data.diameter / 2
                )

        document.saveas(
            "/media/shadkevich/storage_ntfs/virtualbox/common_with_virtualbox/ЧЕРТЕЖИ/MY/"
            + "top.dxf"
        )

    # вспомогательные методы стоек
    # -------------------------------------------------------------------------

    def _draw_stand_platband(
        self,
        data: PlatbandPostInternalSchema,
        numbers: list[str],
        side: SideEnum,
    ) -> None:
        document, model_space = self.get_document_and_model_space()

        # контур
        contour_coordinates = self._get_stand_contour_coordinates(
            data=data, side=side
        )
        model_space.add_polyline2d(points=contour_coordinates, close=True)

        # отверстие под крепления
        if self.holes_data.diameter:
            coordinates_holes_stands = self._get_stand_coordinates_holes(
                side=side
            )
            for coordinate in coordinates_holes_stands:
                model_space.add_circle(
                    center=coordinate, radius=self.holes_data.diameter / 2
                )

        # отверстие под кнопку
        if data.button_hole:
            coordinates_button_hole = self._get_button_hole_coordinates(
                data=data, side=side
            )
            model_space.add_polyline2d(
                points=coordinates_button_hole, close=True
            )

        document.saveas(
            "/media/shadkevich/storage_ntfs/virtualbox/common_with_virtualbox/ЧЕРТЕЖИ/MY/"
            + self._get_stand_file_name(data=data, numbers=numbers, side=side)
        )

    @staticmethod
    def _select_func_side(
        side: SideEnum,
    ) -> Callable[[float | int], float | int]:
        match side:
            case side.LEFT | side.IDENTICAL:
                return lambda x: x
            case side.RIGHT:
                return lambda x: -x
            case _:
                assert_never(side)

    def _get_stand_contour_coordinates(
        self, data: PlatbandPostInternalSchema, side: SideEnum
    ) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        func_side = self._select_func_side(side)

        width = (
            data.depth
            + data.width
            + self.thickness_frames
            - self._inaccuracy_steel_reamer
        )
        height = self.height_platband_stands

        p1 = self.ZERO_POINT
        p2 = Vec2(p1.x, p1.y + height)

        p3_x = p2.x + func_side(width)
        p3 = Vec2(p3_x, p2.y)

        p4 = Vec2(p3.x, p3.y - height)

        return p1, p2, p3, p4

    def _get_button_hole_coordinates(
        self, data: PlatbandPostInternalSchema, side: SideEnum
    ) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        func_side = self._select_func_side(side)

        width_hole, height_hole = map(float, data.button_hole.split("*"))

        if self.holes_data.button_hole_x_center_coordinate:
            x1_delta = (
                self.holes_data.button_hole_x_center_coordinate
                + width_hole / 2
            )
        else:
            # по умолчанию посередине стойки
            x1_delta = data.width / 2 + width_hole / 2
        x1 = func_side(
            self.thickness_frames + x1_delta - self._inaccuracy_steel_reamer
        )

        if self.holes_data.button_hole_y_center_coordinate:
            y1 = (
                self.holes_data.button_hole_y_center_coordinate
                - height_hole / 2
            )
        else:
            # по умолчанию 1250 мм от пола
            y1 = 1250 - height_hole / 2

        p1 = Vec2(x1, y1)
        p2 = Vec2(p1.x, p1.y + height_hole)
        p3 = Vec2(p2.x + func_side(width_hole), p2.y)
        p4 = Vec2(p3.x, p3.y - height_hole)

        return p1, p2, p3, p4

    def _get_stand_coordinates_holes(
        self, side: SideEnum
    ) -> tuple[Vec2, Vec2, Vec2]:
        func_side = self._select_func_side(side)

        y_top = self.height_platband_stands - self.holes_data.top
        y_middle = self.ZERO_POINT.y + self.holes_data.middle
        y_bottom = self.holes_data.bottom

        x_delta = (
            self.thickness_frames
            + self.holes_data.from_edge
            - self._inaccuracy_steel_reamer
        )
        x_coord = self.ZERO_POINT.x + func_side(x_delta)

        result = tuple(Vec2(x_coord, y) for y in (y_top, y_middle, y_bottom))

        return cast(tuple[Vec2, Vec2, Vec2], result)

    @staticmethod
    def _get_stand_file_name(
        data: PlatbandPostInternalSchema, numbers: list[str], side: SideEnum
    ) -> str:
        if side != side.IDENTICAL:
            side_output = f"_{side}"
        else:
            side_output = ""

        return (
            f"{len(numbers)}шт{side_output}"
            f"_глубина-{int(data.depth)}"
            f"_ширина-{int(data.width)}"
            f".dxf"
        )