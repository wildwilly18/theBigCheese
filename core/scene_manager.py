from __future__ import annotations

from typing import Any

from core.scene import BaseScene


class SceneManager:
    def __init__(self, screen: Any) -> None:
        self.screen = screen
        self.scenes: dict[str, BaseScene] = {}
        self.current_scene: BaseScene | None = None
        self.current_name: str | None = None
        self.running = True

    def register_scene(self, name: str, scene: BaseScene) -> None:
        self.scenes[name] = scene

    def change_scene(self, name: str, payload: dict[str, Any] | None = None) -> None:
        if name not in self.scenes:
            raise ValueError(f"Unknown scene '{name}'")

        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = self.scenes[name]
        self.current_name = name
        self.current_scene.on_enter(payload)

    def handle_event(self, event: Any) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            print(f"Current Scene : {type(self.current_scene).__name__}")
            self.current_scene.update(dt)

    def draw(self) -> None:
        if self.current_scene is not None:
            self.current_scene.draw(self.screen)

    def stop(self) -> None:
        self.running = False
