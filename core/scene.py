from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.scene_manager import SceneManager


class BaseScene:
    """Base interface for all scenes."""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__class__.__name__

    def on_enter(self, payload: Optional[dict[str, Any]] = None) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: Any) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: Any) -> None:
        pass
