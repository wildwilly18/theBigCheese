from __future__ import annotations

from entities.base_entity import BaseEntity


class Player(BaseEntity):
    """User-controlled entity driven directly by scene input."""

    def __init__(self, x: float, y: float, yaw_rad: float = 0.0) -> None:
        super().__init__(x, y, yaw_rad=yaw_rad)

    def update(self, v_cmd: float, omega_cmd: float, dt: float) -> None:
        self._kinematic_update(float(v_cmd), float(omega_cmd), float(dt))