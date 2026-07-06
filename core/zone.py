from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass
class Zone:
    points: Iterable[Sequence[float]]
    exclusion: bool
    num_points: int = field(init=False)

    def __post_init__(self):
        normalized = []
        for raw_point in self.points:
            normalized.append(self._coerce_point(raw_point, name="points item"))

        if len(normalized) < 3:
            raise ValueError("points must contain at least 3 (x, y) coordinates")

        self.num_points = len(normalized)
        self.points = tuple(normalized)

    def point_in_polygon(self, point):
        p = self._coerce_point(point, name="point")

        poly = self.points
        n = len(poly)

        # Dan Sunday's winding number algorithm.
        # Non-zero winding number => point is inside.
        wn = 0

        for i in range(n):
            v1 = poly[i]
            v2 = poly[(i + 1) % n]

            # If point lies exactly on an edge, count it as inside.
            if self._point_on_segment(v1, v2, p):
                return True

            if v1[1] <= p[1]:
                if v2[1] > p[1] and self._is_left(v1, v2, p) > 0:
                    wn += 1
            else:
                if v2[1] <= p[1] and self._is_left(v1, v2, p) < 0:
                    wn -= 1

        return wn != 0

    @staticmethod
    def _is_left(v1, v2, p):
        return (v2[0] - v1[0]) * (p[1] - v1[1]) - (p[0] - v1[0]) * (v2[1] - v1[1])

    @staticmethod
    def _point_on_segment(v1, v2, p, eps=1e-12):
        cross = (v2[0] - v1[0]) * (p[1] - v1[1]) - (p[0] - v1[0]) * (v2[1] - v1[1])
        if abs(cross) > eps:
            return False

        min_x = min(v1[0], v2[0]) - eps
        max_x = max(v1[0], v2[0]) + eps
        min_y = min(v1[1], v2[1]) - eps
        max_y = max(v1[1], v2[1]) + eps
        return min_x <= p[0] <= max_x and min_y <= p[1] <= max_y

    @staticmethod
    def _coerce_point(value, name="point"):
        try:
            x, y = value
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be an (x, y) coordinate") from None

        try:
            return (float(x), float(y))
        except (TypeError, ValueError):
            raise ValueError(f"{name} must contain numeric x and y values") from None



