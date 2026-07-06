from __future__ import annotations

import pygame

from core.scene import BaseScene
from core.world import WorldView
from entities.actor import Actor


class HomeBaseScene(BaseScene):
    """Renders a fixed 10m x 10m base in meter coordinates."""

    def __init__(self, manager, game_state) -> None:
        super().__init__(manager)
        self.game_state = game_state
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)
        spawn = self.game_state.home_base_size_m / 2.0
        self.actor = Actor(spawn, spawn, yaw_rad=0.0)
        self.move_speed_mps = 3.0
        self.turn_speed_rps = 2.8

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                self.manager.change_scene("level")
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

        self.actor.update(v_mps, omega_rps, dt)
        size_m = self.game_state.home_base_size_m
        self.actor.clamp_to_bounds(0.0, size_m, 0.0, size_m)

    def draw(self, screen) -> None:
        screen.fill((20, 34, 28))

        size_m = self.game_state.home_base_size_m
        view = WorldView(size_m, size_m, screen.get_rect(), padding_px=140)
        base_rect = view.rect_to_screen(0, 0, size_m, size_m)

        pygame.draw.rect(screen, (48, 90, 65), base_rect)
        pygame.draw.rect(screen, (210, 230, 220), base_rect, width=3)

        self._draw_meter_grid(screen, view, size_m)
        self.actor.draw(screen, view)
        self._draw_ui(screen)

    def _draw_meter_grid(self, screen, view: WorldView, size_m: float) -> None:
        for meter in range(1, int(size_m)):
            x, y0 = view.to_screen(float(meter), 0.0)
            _, y1 = view.to_screen(float(meter), size_m)
            pygame.draw.line(screen, (88, 122, 104), (x, y0), (x, y1), 1)

            x0, y = view.to_screen(0.0, float(meter))
            x1, _ = view.to_screen(size_m, float(meter))
            pygame.draw.line(screen, (88, 122, 104), (x0, y), (x1, y), 1)

    def _draw_ui(self, screen) -> None:
        title = self.font.render("Home Base (10m x 10m)", True, (236, 244, 240))
        line1 = self.small_font.render("L: Deploy to Level", True, (225, 235, 228))
        line2 = self.small_font.render("M: Back to Menu", True, (225, 235, 228))
        line3 = self.small_font.render("W/S: Move   A/D: Turn", True, (225, 235, 228))
        line4 = self.small_font.render("Esc: Quit", True, (225, 235, 228))

        screen.blit(title, (24, 18))
        screen.blit(line1, (24, 52))
        screen.blit(line2, (24, 78))
        screen.blit(line3, (24, 104))
        screen.blit(line4, (24, 130))
