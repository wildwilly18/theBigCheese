from __future__ import annotations

import math
from enum import Enum
from typing import Optional

import numpy as np

from core.map import Map
from entities.base_entity import BaseEntity


class NPCState(Enum):
    Idle = 0
    Moving = 1
    Tracking = 2


class NPC(BaseEntity):
    """Autonomous entity that follows a planned path in map space."""

    def __init__(self, active_map: Map, id: int, x: float, y: float, psi: float, path_init: Optional[np.ndarray] = None) -> None:
        super().__init__(x, y, yaw_rad=psi, color_scheme=1)
        self.active_map = active_map
        self.id = int(id)

        self.v = 0.0
        self.omega = 0.0
        self.a_max = 1.0
        self.alpha_max = 3.0
        self.heading_time_constant_s = 0.12
        self.max_turn_rate_rps = 8.0
        self.wp_accept_dist = 0.2
        self.state = NPCState.Idle
        self._path = np.empty((0, 2), dtype=float)
        self.path = path_init

    @property
    def path(self) -> np.ndarray:
        return self._path

    @path.setter
    def path(self, value: Optional[np.ndarray]) -> None:
        if value is None or (isinstance(value, np.ndarray) and value.size == 0):
            self._path = np.empty((0, 2), dtype=float)
        else:
            arr = np.asarray(value, dtype=float)
            if arr.ndim != 2 or arr.shape[1] != 2:
                raise ValueError("path must be an (n, 2) array of x,y waypoints")
            self._path = arr
        self.state = NPCState.Moving if len(self._path) > 0 else NPCState.Idle

    @property
    def current_waypoint(self) -> Optional[tuple[float, float]]:
        if len(self.path) == 0:
            return None
        return (float(self.path[0, 0]), float(self.path[0, 1]))

    @property
    def wpt_heading(self) -> Optional[float]:
        wp = self.current_waypoint
        if wp is None:
            return None
        return math.atan2(wp[1] - self.y, wp[0] - self.x)

    def update(self, dt: float = 0.01) -> None:
        if self.state != NPCState.Moving:
            return

        v_cmd, omega_cmd = self._follow_path_controller()
        self._kinematic_update(v_cmd, omega_cmd, dt)

    def _follow_path_controller(self) -> tuple[float, float]:
        wp = self.current_waypoint

        if wp is None:
            self.state = NPCState.Idle
            return (0.0, 0.0)

        dist = math.hypot(wp[0] - self.x, wp[1] - self.y)
        if dist < self.wp_accept_dist:
            self.path = self.path[1:]
            return (0.0, 0.0)

        heading = self.wpt_heading
        if heading is None:
            return (0.0, 0.0)

        head_err = self.small_angle_diff(heading, self.psi)

        v_cmd = max(-1.5 * (head_err ** 2) + 2, 0.35)
        omega_cmd = head_err / self.heading_time_constant_s
        omega_cmd = max(-self.max_turn_rate_rps, min(self.max_turn_rate_rps, omega_cmd))
        return (v_cmd, omega_cmd)