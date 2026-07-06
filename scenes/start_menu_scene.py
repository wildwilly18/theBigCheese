from __future__ import annotations

import pygame

from core.scene import BaseScene


class StartMenuScene(BaseScene):
    def __init__(self, manager, game_state) -> None:
        super().__init__(manager)
        self.game_state = game_state
        self.title_font = pygame.font.SysFont(None, 72)
        self.body_font = pygame.font.SysFont(None, 34)

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.manager.change_scene("home_base")
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.manager.stop()

    def draw(self, screen) -> None:
        screen.fill((15, 18, 32))

        title = self.title_font.render("THE BIG CHEESE", True, (245, 232, 180))
        subtitle = self.body_font.render("Press Enter to Start", True, (220, 225, 235))
        help_line = self.body_font.render("Esc or Q to Quit", True, (190, 200, 215))

        title_rect = title.get_rect(center=(screen.get_width() // 2, 250))
        sub_rect = subtitle.get_rect(center=(screen.get_width() // 2, 360))
        help_rect = help_line.get_rect(center=(screen.get_width() // 2, 410))

        screen.blit(title, title_rect)
        screen.blit(subtitle, sub_rect)
        screen.blit(help_line, help_rect)
