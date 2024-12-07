class GetCoordinatesAngleLineSuccess:
    """Кейсы получения координат линии под углом."""

    ReturnType = tuple[int, tuple[int, int], float]
    ANGLE = 63
    A = 1
    B = 2
    HYPOTENUSE = (A**2 + B**2) ** 0.5

    def case_first_quarter(self) -> ReturnType:
        """Первая четверть."""
        return self.ANGLE, (self.A, self.B), self.HYPOTENUSE

    def case_second_quarter(self) -> ReturnType:
        """Вторая четверть."""
        return 90 + self.ANGLE, (-self.B, self.A), self.HYPOTENUSE

    def case_third_quarter(self) -> ReturnType:
        """Третья четверть."""
        return 180 + self.ANGLE, (-self.A, -self.B), self.HYPOTENUSE

    def case_fourth_quarter(self) -> ReturnType:
        """Четвёртая четверть."""
        return 270 + self.ANGLE, (self.B, -self.A), self.HYPOTENUSE
