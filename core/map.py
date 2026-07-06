import json
import os
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from core.zone import Zone


@dataclass
class Map:
    """Map containing one boundary polygon and zero or more exclusion polygons.

    Attributes:
        grid_map   -- bool ndarray (rows, cols): True = inside contain and not inside any exclusion.
        grid_d2b   -- float ndarray (rows, cols): distance from each cell centre to the nearest
                    polygon edge (contain boundary or any exclusion boundary).
        x_breakpoints / y_breakpoints -- 1-D arrays of cell-centre coordinates.
    """

    json_data: Any
    grid_resolution: float = 0.02
    zones: list[Zone] = field(init=False)
    contain_zone: Zone = field(init=False)
    exclusion_zones: list[Zone] = field(init=False)
    x_breakpoints: np.ndarray = field(init=False)
    y_breakpoints: np.ndarray = field(init=False)
    grid_map: np.ndarray = field(init=False)
    grid_d2b: np.ndarray = field(init=False)

    def __post_init__(self):
        payload = self._load_payload(self.json_data)

        contain_points = self._get_required(payload, ["contain", "contain_zone", "containZone"])
        exclusion_polygons = self._get_optional(
            payload,
            ["exclusions", "exclusion_zones", "exclusionZones", "exlcusions", "exlcusion_zones"],
            default=[],
        )

        self.contain_zone = Zone(points=contain_points, exclusion=False)
        self.exclusion_zones = [Zone(points=poly, exclusion=True) for poly in exclusion_polygons]
        self.zones = [self.contain_zone, *self.exclusion_zones]

        self._build_grids()

    def x_y_from_idx(self, x_idx: int, y_idx: int | None = None) -> tuple[float, float]:
        """Return map-space (x, y) from either flat idx or x/y grid indices."""
        if y_idx is None:
            num_y_bpts = len(self.y_breakpoints)
            xx = x_idx // num_y_bpts
            yy = x_idx % num_y_bpts
        else:
            xx = x_idx
            yy = y_idx

        in_bounds = 0 <= xx < len(self.x_breakpoints) and 0 <= yy < len(self.y_breakpoints)
        if not in_bounds:
            raise IndexError("grid index out of bounds")

        return (float(self.x_breakpoints[xx]), float(self.y_breakpoints[yy]))

    def idx_idy_from_xy(self, x: float, y: float) -> tuple[int, int]:
        """Return nearest x/y grid indices for a map-space (x, y) point."""
        if len(self.x_breakpoints) == 0 or len(self.y_breakpoints) == 0:
            raise ValueError("grid breakpoints are empty")

        if x < self.x_breakpoints[0] or x > self.x_breakpoints[-1]:
            raise IndexError("x coordinate out of bounds")
        if y < self.y_breakpoints[0] or y > self.y_breakpoints[-1]:
            raise IndexError("y coordinate out of bounds")

        idx = int(np.abs(self.x_breakpoints - x).argmin())
        idy = int(np.abs(self.y_breakpoints - y).argmin())
        return (idx, idy)

    
    def point_in_zone(self, x_idx: int, y_idx: int | None = None) -> bool:
        """Return True when a grid cell is inside the valid map area.

        Supports either:
        - point_in_zone(flat_idx)
        - point_in_zone(x_idx, y_idx)
        """
        if y_idx is None:
            num_y_bpts = len(self.y_breakpoints)
            xx = x_idx // num_y_bpts
            yy = x_idx % num_y_bpts
        else:
            xx = x_idx
            yy = y_idx

        in_bounds = 0 <= xx < len(self.x_breakpoints) and 0 <= yy < len(self.y_breakpoints)
        if not in_bounds:
            return False

        # Underlying NumPy storage is [row, col] -> [y_idx, x_idx].
        # Flat-index conversion above follows column-major convention: x-major.
        return bool(self.grid_map[yy, xx])

    def _build_grids(self):
        pts = np.array(self.contain_zone.points)
        x_min, y_min = pts[:, 0].min(), pts[:, 1].min()
        x_max, y_max = pts[:, 0].max(), pts[:, 1].max()

        res = self.grid_resolution
        self.x_breakpoints = np.arange(x_min + res / 2, x_max, res)
        self.y_breakpoints = np.arange(y_min + res / 2, y_max, res)

        # Build (rows, cols) meshgrid; row index = y, col index = x.
        xx, yy = np.meshgrid(self.x_breakpoints, self.y_breakpoints)
        shape = xx.shape

        # Flatten to list of points for zone checks.
        pts_flat = list(zip(xx.ravel().tolist(), yy.ravel().tolist()))

        # grid_map: True where inside contain and not inside any exclusion.
        in_contain = np.array([self.contain_zone.point_in_polygon(p) for p in pts_flat])
        in_exclusion = np.zeros(len(pts_flat), dtype=bool)
        for ex_zone in self.exclusion_zones:
            in_exclusion |= np.array([ex_zone.point_in_polygon(p) for p in pts_flat])

        self.grid_map = (in_contain & ~in_exclusion).reshape(shape)

        # grid_d2b: minimum distance from each cell centre to any polygon edge.
        all_edges = self._collect_edges()
        self.grid_d2b = self._min_edge_distances(xx, yy, all_edges)

    def _collect_edges(self) -> list[tuple]:
        """Return every polygon edge across all zones as (v1, v2) tuples."""
        edges = []
        for zone in self.zones:
            poly = zone.points
            n = len(poly)
            for i in range(n):
                edges.append((poly[i], poly[(i + 1) % n]))
        return edges

    @staticmethod
    def _min_edge_distances(xx: np.ndarray, yy: np.ndarray, edges: list) -> np.ndarray:
        """Vectorised point-to-segment distance for every cell against every edge."""
        px = xx.ravel()
        py = yy.ravel()
        n_pts = len(px)
        min_dist = np.full(n_pts, np.inf)

        for (ax, ay), (bx, by) in edges:
            dx, dy = bx - ax, by - ay
            seg_len_sq = dx * dx + dy * dy

            if seg_len_sq == 0.0:
                # Degenerate edge (zero length) — use distance to the point.
                d = np.hypot(px - ax, py - ay)
            else:
                # Project each grid point onto the segment, clamped to [0, 1].
                t = np.clip(((px - ax) * dx + (py - ay) * dy) / seg_len_sq, 0.0, 1.0)
                cx = ax + t * dx
                cy = ay + t * dy
                d = np.hypot(px - cx, py - cy)

            np.minimum(min_dist, d, out=min_dist)

        return min_dist.reshape(xx.shape)

    @staticmethod
    def _load_payload(value):
        if isinstance(value, str):
            if os.path.isfile(value):
                with open(value, "r", encoding="utf-8") as f:
                    return json.load(f)
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("json_data must be a valid JSON string or a path to a JSON file") from exc

        if isinstance(value, dict):
            return value

        raise ValueError("json_data must be a JSON string, file path, or dict")

    @staticmethod
    def _get_required(payload, keys):
        for key in keys:
            if key in payload:
                return payload[key]
        joined_keys = ", ".join(keys)
        raise ValueError(f"missing required contain polygon key; expected one of: {joined_keys}")

    @staticmethod
    def _get_optional(payload, keys, default):
        for key in keys:
            if key in payload:
                return payload[key]
        return default
