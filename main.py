import pygame
from core.game_state import GameState
from core.scene_manager import SceneManager
from scenes.home_base_scene import HomeBaseScene
from scenes.level_scene import LevelScene
from scenes.start_menu_scene import StartMenuScene
from settings import WIDTH, HEIGHT, FPS

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Big Cheese")
clock = pygame.time.Clock()

game_state = GameState()
scene_manager = SceneManager(screen)

scene_manager.register_scene("start_menu", StartMenuScene(scene_manager, game_state))
scene_manager.register_scene("home_base", HomeBaseScene(scene_manager, game_state))
scene_manager.register_scene("level", LevelScene(scene_manager, game_state))
scene_manager.change_scene("start_menu")

while scene_manager.running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            scene_manager.stop()
            continue
        scene_manager.handle_event(event)

    scene_manager.update(dt)
    scene_manager.draw()

    pygame.display.flip()

pygame.quit()