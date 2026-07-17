from __future__ import annotations

import math

import pygame


class BaseEntity:
    """Shared transform, movement, and rendering behavior for movable entities."""

    def __init__(self, x: float, y: float, yaw_rad: float = 0.0, color_scheme: int = 0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.psi = float(yaw_rad)

        if color_scheme == 0:
            self.body_color = (245, 188, 100)
            self.marker_color = (42, 56, 84)
        elif color_scheme == 1:
            self.body_color = (235, 70, 90)
            self.marker_color = (255, 215, 225)
        else:
            self.body_color = (245, 245, 245)
            self.marker_color = (120, 120, 120)


    @property
    def x_m(self) -> float:
        return self.x

    @x_m.setter
    def x_m(self, value: float) -> None:
        self.x = float(value)

    @property
    def y_m(self) -> float:
        return self.y

    @y_m.setter
    def y_m(self, value: float) -> None:
        self.y = float(value)

    @property
    def yaw_rad(self) -> float:
        return self.psi

    @yaw_rad.setter
    def yaw_rad(self, value: float) -> None:
        self.psi = float(value)

    def clamp_to_bounds(self, min_x: float, max_x: float, min_y: float, max_y: float) -> None:
        self.x = min(max(self.x, min_x), max_x)
        self.y = min(max(self.y, min_y), max_y)

    def draw(
        self,
        screen: pygame.Surface,
        view,
        body_color: tuple[int, int, int] | None = None,
        marker_color: tuple[int, int, int] | None = None,
    ) -> None:
        body_color = self.body_color if body_color is None else body_color
        marker_color = self.marker_color if marker_color is None else marker_color

        x_px, y_px = view.to_screen(self.x, self.y)
        radius = max(4, int(0.25 * view.pixels_per_meter))
        pygame.draw.circle(screen, body_color, (x_px, y_px), radius)

        heading_len = max(6, int(radius * 1.4))
        hx = int(x_px + math.cos(self.psi) * heading_len)
        hy = int(y_px + math.sin(self.psi) * heading_len)
        pygame.draw.line(screen, marker_color, (x_px, y_px), (hx, hy), 3)

    def _kinematic_update(self, v_cmd: float, omega_cmd: float, dt: float = 0.01) -> None:
        self.psi = self.psi + omega_cmd * dt
        self.psi = (self.psi + math.pi) % (2 * math.pi) - math.pi

        self.x = self.x + math.cos(self.psi) * (v_cmd * dt)
        self.y = self.y + math.sin(self.psi) * (v_cmd * dt)

    @staticmethod
    def small_angle_diff(a: float, b: float) -> float:
        """Return the signed shortest angular difference from b to a, in [-pi, pi]."""
        return (a - b + math.pi) % (2 * math.pi) - math.pi