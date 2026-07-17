from __future__ import annotations

import pygame

from core.map import Map
from core.scene import BaseScene
from core.viewport import MapViewport
from entities.npc import NPCState
from entities.player import Player
from core.orchestrator import Orchestrator


class LevelScene(BaseScene):
    """Level scene with a local 10m x 10m planning map for NPCs."""

    def __init__(self, manager, game_state) -> None:
        super().__init__(manager)
        self.game_state = game_state
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)
        self.player = Player(0.0, 0.0, yaw_rad=0.0)
        self.move_speed_mps = 4.0
        self.turn_speed_rps = 3.0

        self.level_map_size_m = 40.0
        self.level_map = self._build_level_map()

        self._spawn_actor_in_level()

    def on_enter(self, payload=None) -> None:
        self._spawn_actor_in_level()
        self._setup_enemy_orchestrator()

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

        for enemy in self.enemies.actors:
            if enemy.state == NPCState.Idle:
                self.enemies.plan_actor_to_goal(enemy.id, self.player.x_m, self.player.y_m)
        self.enemies.loop(dt)
        self.player.update(v_mps, omega_rps, dt)

        world_width_m, world_height_m = self._world_size_m()
        self.player.clamp_to_bounds(0.0, world_width_m, 0.0, world_height_m)

    def draw(self, screen) -> None:
        screen.fill((24, 24, 30))

        world_width_m, world_height_m = self._world_size_m()

        view = MapViewport(world_width_m, world_height_m, screen.get_rect(), padding_px=130)

        rect = view.rect_to_screen(0.0, 0.0, world_width_m, world_height_m)
        pygame.draw.rect(screen, (64, 76, 112), rect)
        pygame.draw.rect(screen, (210, 220, 255), rect, width=2)

        self._draw_enemy_paths(screen, view)
        self.player.draw(screen, view, body_color=(245, 188, 100), marker_color=(42, 56, 84))
        for enemy in self.enemies.actors:
            enemy.draw(screen, view)

        self._draw_ui(screen)

    def _build_level_map(self) -> Map:
        size = self.level_map_size_m
        payload = {
            "contain": [[0.0, 0.0], [size, 0.0], [size, size], [0.0, size]],
            "exclusions": [],
        }
        return Map(payload, grid_resolution=0.04)

    def _world_size_m(self) -> tuple[float, float]:
        return (self.level_map_size_m, self.level_map_size_m)

    def _spawn_actor_in_level(self) -> None:
        world_width_m, world_height_m = self._world_size_m()
        self.player.x_m = world_width_m * 0.5
        self.player.y_m = world_height_m * 0.5
        self.player.yaw_rad = 0.0

    def _setup_enemy_orchestrator(self) -> None:
        self.enemies = Orchestrator(map=self.level_map, player=self.player)

        self.enemies.add_actor(0, 2.0, 20.0, 0.0)

    def _draw_enemy_paths(self, screen, view) -> None:
        for enemy in self.enemies.actors:
            if len(enemy.path) == 0:
                continue

            points_px = [view.to_screen(float(x), float(y)) for x, y in enemy.path]

            if len(points_px) > 1:
                pygame.draw.lines(screen, (255, 168, 180), False, points_px, 2)

            for i, p in enumerate(points_px):
                radius = 2 if i == 0 else 3
                color = (255, 220, 226) if i == 0 else (255, 185, 196)
                pygame.draw.circle(screen, color, p, radius)


    def _draw_ui(self, screen) -> None:
        title = self.font.render("Level Scene (10m x 10m Map)", True, (235, 240, 252))
        details = self.small_font.render(
            "NPCs plan paths on local map",
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
