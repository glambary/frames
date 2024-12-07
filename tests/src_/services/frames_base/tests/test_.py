from pytest_cases import parametrize_with_cases
from src_.services.frames_base.test_cases.t_cases import (
    GetCoordinatesAngleLineSuccess,
)

from services.frames.frames_base import FramesBase


@parametrize_with_cases(
    argnames=[
        "angle",
        "expected_coordinates",
        "length",
    ],
    cases=GetCoordinatesAngleLineSuccess,
)
def test__success(
    angle: float,
    expected_coordinates: tuple[float, float],
    length: float,
):
    res = FramesBase.get_coordinates_angle_line(
        FramesBase.ZERO_POINT, angle, length
    )
    x = abs(res[0] - expected_coordinates[0])
    y = abs(res[1] - expected_coordinates[1])
    assert x <= 0.1
    assert y <= 0.1
