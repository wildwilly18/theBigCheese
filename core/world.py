from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

import pygame


@dataclass
class WorldView:
    """Maps meter-space coordinates into pixels while fitting inside the screen."""

    world_width_m: float
    world_height_m: float
    screen_rect: pygame.Rect
    padding_px: int = 60

    def __post_init__(self) -> None:
        drawable_width = max(1, self.screen_rect.width - (self.padding_px * 2))
        drawable_height = max(1, self.screen_rect.height - (self.padding_px * 2))
        self.pixels_per_meter = min(
            drawable_width / max(self.world_width_m, 0.001),
            drawable_height / max(self.world_height_m, 0.001),
        )

        content_width_px = self.world_width_m * self.pixels_per_meter
        content_height_px = self.world_height_m * self.pixels_per_meter
        self.origin_x = self.screen_rect.centerx - (content_width_px / 2)
        self.origin_y = self.screen_rect.centery - (content_height_px / 2)

    def to_screen(self, x_m: float, y_m: float) -> tuple[int, int]:
        x_px = self.origin_x + (x_m * self.pixels_per_meter)
        y_px = self.origin_y + (y_m * self.pixels_per_meter)
        return int(x_px), int(y_px)

    def rect_to_screen(self, x_m: float, y_m: float, w_m: float, h_m: float) -> pygame.Rect:
        x_px, y_px = self.to_screen(x_m, y_m)
        w_px = max(1, int(w_m * self.pixels_per_meter))
        h_px = max(1, int(h_m * self.pixels_per_meter))
        return pygame.Rect(x_px, y_px, w_px, h_px)


def generate_block_layout(block_count: int = 8, rng: random.Random | None = None) -> set[tuple[int, int]]:
    """Create an adjacent set of 10m x 10m block coordinates via random walk."""

    rng = rng or random.Random()
    blocks: set[tuple[int, int]] = {(0, 0)}
    frontier = [(0, 0)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while len(blocks) < block_count:
        base_x, base_y = rng.choice(frontier)
        dx, dy = rng.choice(directions)
        candidate = (base_x + dx, base_y + dy)
        blocks.add(candidate)
        frontier = list(blocks)

    return blocks


def block_bounds(blocks: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    xs = [x for x, _ in blocks]
    ys = [y for _, y in blocks]
    return min(xs), max(xs), min(ys), max(ys)
