from collections import defaultdict
from typing import assert_never

from ezdxf.math import Vec2

from exception.custom import ValueFromUserError
from schemas.frames_common.enums import SideEnum, ThicknessEnum
from schemas.frames_one_fold.input import (
    FramesOneFoldInputSchema,
    HolesInputSchema,
)
from schemas.frames_one_fold.internal import PlatbandPostInternalSchema
from services.frames_base import FramesBase


class FramesOneFold(FramesBase):
    SUPPORTED_THICKNESS = {ThicknessEnum.ONE_POINT_ZERO}
    # погрешность развёртки стали
    INACCURACY_STEEL_REAMER = {ThicknessEnum.ONE_POINT_ZERO: 3.63}

    def __init__(
        self,
        *,
        thickness_frames: float,
        holes_data: HolesInputSchema,
        **kwargs,
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
        need_to_grouped: False,
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

        for data, numbers in left_platbands.items():
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
        document.saveas("")

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
        ...

        document.saveas(
            self._get_stand_file_name(data=data, numbers=numbers, side=side)
        )

    def _get_stand_contour_coordinates(
        self, data: PlatbandPostInternalSchema, side: SideEnum
    ) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        width = (
            data.depth
            + data.width
            + self.thickness_frames
            - self._inaccuracy_steel_reamer
        )
        height = self.height_platband_stands

        p1 = self.ZERO_POINT
        p2 = Vec2(p1.x, p1.y + height)

        if side in (SideEnum.LEFT, SideEnum.IDENTICAL):
            p3_x = p2.x + width
        elif side == SideEnum.RIGHT:
            p3_x = p2.x - width
        else:
            raise assert_never(side)
        p3 = Vec2(p3_x, p2.y)

        p4 = Vec2(p3.x, p3.y - height)

        return p1, p2, p3, p4

    def _check_holes(self, holes_data: HolesInputSchema) -> tuple[bool, bool]:
        pass

    @staticmethod
    def _get_stand_file_name(
        data: PlatbandPostInternalSchema, numbers: list[str], side: SideEnum
    ) -> str:
        if side != side.IDENTICAL:
            side_output = f"_{side}"
        else:
            side_output = ""

        return (
            f"{len(numbers)}{side_output}"
            f"_глубина-{data.depth}"
            f"_ширина-{data.width}"
        )

    def _get_stand_coordinates_holes(
        self, side: str
    ) -> tuple[Vec2, Vec2, Vec2]:
        y_top = self.height_platband_stands - self.holes_data.top
        y_middle = self.ZERO_POINT.y + self.holes_data.middle
        y_bottom = self.height_platband_stands + self.holes_data.bottom

        x_delta = (
            self.thickness_frames
            + self.holes_data.from_edge
            - self._inaccuracy_steel_reamer
        )

        if side in (SideEnum.LEFT, SideEnum.IDENTICAL):
            x_coord = self.ZERO_POINT.x + x_delta
        elif side == SideEnum.RIGHT:
            x_coord = self.ZERO_POINT.x - x_delta
        else:
            raise assert_never(side)

        return tuple(Vec2(x=x_coord, y=y) for y in (y_top, y_middle, y_bottom))
