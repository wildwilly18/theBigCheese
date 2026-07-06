from __future__ import annotations

import pygame

from core.scene import BaseScene
from core.viewport import MapViewport, block_bounds
from entities.player import Player


class LevelScene(BaseScene):
    """Displays a modular level composed of adjacent 10m x 10m blocks."""

    def __init__(self, manager, game_state) -> None:
        super().__init__(manager)
        self.game_state = game_state
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)
        self.player = Player(0.0, 0.0, yaw_rad=0.0)
        self.move_speed_mps = 4.0
        self.turn_speed_rps = 3.0
        self.game_state.level_layout_blocks = self._fixed_3x3_layout()
        self._spawn_actor_in_level()

    def on_enter(self, payload=None) -> None:
        self.game_state.level_layout_blocks = self._fixed_3x3_layout()
        self._spawn_actor_in_level()

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                self.manager.change_scene("home_base")
            elif event.key == pygame.K_m:
                self.manager.change_scene("start_menu")
            elif event.key == pygame.K_ESCAPE:
                self.manager.stop()

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        v_mps = 0.0
        omega_rps = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            v_mps += self.move_speed_mps
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            v_mps -= self.move_speed_mps
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            omega_rps -= self.turn_speed_rps
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            omega_rps += self.turn_speed_rps

        self.player.update(v_mps, omega_rps, dt)
        world_width_m, world_height_m = self._world_size_m()
        self.player.clamp_to_bounds(0.0, world_width_m, 0.0, world_height_m)

    def draw(self, screen) -> None:
        screen.fill((24, 24, 30))

        blocks = self.game_state.level_layout_blocks
        block_size_m = self.game_state.world_units_per_block

        min_x, max_x, min_y, max_y = block_bounds(blocks)
        world_width_m = (max_x - min_x + 1) * block_size_m
        world_height_m = (max_y - min_y + 1) * block_size_m

        view = MapViewport(world_width_m, world_height_m, screen.get_rect(), padding_px=130)

        for bx, by in blocks:
            x_m = (bx - min_x) * block_size_m
            y_m = (by - min_y) * block_size_m
            rect = view.rect_to_screen(x_m, y_m, block_size_m, block_size_m)
            pygame.draw.rect(screen, (64, 76, 112), rect)
            pygame.draw.rect(screen, (210, 220, 255), rect, width=2)

        self.player.draw(screen, view, body_color=(245, 188, 100), marker_color=(42, 56, 84))

        self._draw_ui(screen, len(blocks), block_size_m)

    @staticmethod
    def _fixed_3x3_layout() -> list[tuple[int, int]]:
        return [(x, y) for y in range(3) for x in range(3)]

    def _world_size_m(self) -> tuple[float, float]:
        blocks = self.game_state.level_layout_blocks
        block_size_m = self.game_state.world_units_per_block
        min_x, max_x, min_y, max_y = block_bounds(blocks)
        world_width_m = (max_x - min_x + 1) * block_size_m
        world_height_m = (max_y - min_y + 1) * block_size_m
        return world_width_m, world_height_m

    def _spawn_actor_in_level(self) -> None:
        world_width_m, world_height_m = self._world_size_m()
        self.player.x_m = world_width_m * 0.5
        self.player.y_m = world_height_m * 0.5
        self.player.yaw_rad = 0.0

    def _draw_ui(self, screen, block_count: int, block_size_m: float) -> None:
        title = self.font.render("Level Scene (Modular Blocks)", True, (235, 240, 252))
        details = self.small_font.render(
            f"{block_count} blocks, each {block_size_m:.0f}m x {block_size_m:.0f}m",
            True,
            (217, 225, 245),
        )
        line1 = self.small_font.render("B: Return to Home Base", True, (217, 225, 245))
        line2 = self.small_font.render("W/S: Move   A/D: Turn", True, (217, 225, 245))
        line3 = self.small_font.render("M: Back to Menu", True, (217, 225, 245))

        screen.blit(title, (24, 18))
        screen.blit(details, (24, 52))
        screen.blit(line1, (24, 78))
        screen.blit(line2, (24, 104))
        screen.blit(line3, (24, 130))
