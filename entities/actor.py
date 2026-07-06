from __future__ import annotations
import math
import pygame


class Actor:
    """Player actor represented by a 0.5m circle with a yaw marker."""

    def __init__(self, x_m: float, y_m: float, yaw_rad: float = 0.0, radius_m: float = 0.5) -> None:
        self.x_m = x_m
        self.y_m = y_m
        self.yaw_rad = yaw_rad
        self.radius_m = radius_m
        self.v_mps = 0.0
        self.omega_rps = 0.0

    def update(self, v_mps: float, omega_rps: float, dt: float = 1.0) -> None:
        """Integrate position/yaw in meter-space."""

        self.v_mps = v_mps
        self.omega_rps = omega_rps

        self.yaw_rad = self._wrap_angle(self.yaw_rad + (omega_rps * dt))
        self.x_m += v_mps * math.cos(self.yaw_rad) * dt
        self.y_m += v_mps * math.sin(self.yaw_rad) * dt

    def draw(
        self,
        screen: pygame.Surface,
        world_view,
        body_color: tuple[int, int, int] = (233, 205, 91),
        marker_color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """Draw body circle and triangle marker oriented by yaw."""

        cx_px, cy_px = world_view.to_screen(self.x_m, self.y_m)
        radius_px = max(1, int(self.radius_m * world_view.pixels_per_meter))

        pygame.draw.circle(screen, body_color, (cx_px, cy_px), radius_px)

        tip_m = self.radius_m * 1
        base_m = self.radius_m * 0.7
        side_offset = math.radians(140)

        tip = self._point_from_angle(self.x_m, self.y_m, self.yaw_rad, tip_m)
        left = self._point_from_angle(self.x_m, self.y_m, self.yaw_rad + side_offset, base_m)
        right = self._point_from_angle(self.x_m, self.y_m, self.yaw_rad - side_offset, base_m)

        pygame.draw.polygon(
            screen,
            marker_color,
            [
                world_view.to_screen(*tip),
                world_view.to_screen(*left),
                world_view.to_screen(*right),
            ],
        )

    def collides_with_bounds(
        self,
        min_x_m: float,
        max_x_m: float,
        min_y_m: float,
        max_y_m: float,
    ) -> bool:
        """Return True if actor overlaps any map edge."""

        return (
            (self.x_m - self.radius_m) < min_x_m
            or (self.x_m + self.radius_m) > max_x_m
            or (self.y_m - self.radius_m) < min_y_m
            or (self.y_m + self.radius_m) > max_y_m
        )

    def clamp_to_bounds(
        self,
        min_x_m: float,
        max_x_m: float,
        min_y_m: float,
        max_y_m: float,
    ) -> dict[str, bool]:
        """Clamp actor inside bounds and report which edges were touched."""

        touched = {"left": False, "right": False, "top": False, "bottom": False}

        min_center_x = min_x_m + self.radius_m
        max_center_x = max_x_m - self.radius_m
        min_center_y = min_y_m + self.radius_m
        max_center_y = max_y_m - self.radius_m

        if self.x_m < min_center_x:
            self.x_m = min_center_x
            touched["left"] = True
        elif self.x_m > max_center_x:
            self.x_m = max_center_x
            touched["right"] = True

        if self.y_m < min_center_y:
            self.y_m = min_center_y
            touched["top"] = True
        elif self.y_m > max_center_y:
            self.y_m = max_center_y
            touched["bottom"] = True

        return touched

    @staticmethod
    def _wrap_angle(angle_rad: float) -> float:
        return (angle_rad + math.pi) % (2.0 * math.pi) - math.pi

    @staticmethod
    def _point_from_angle(cx_m: float, cy_m: float, angle_rad: float, distance_m: float) -> tuple[float, float]:
        return (
            cx_m + (math.cos(angle_rad) * distance_m),
            cy_m + (math.sin(angle_rad) * distance_m),
        )


# Backward-compatible alias while codebase migrates to Actor naming.
actor = Actor

