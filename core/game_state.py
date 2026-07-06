from dataclasses import dataclass, field


@dataclass
class GameState:
    """Persistent game data shared across scenes."""

    world_units_per_block: float = 10.0
    home_base_size_m: float = 10.0
    level_block_count: int = 8
    level_layout_blocks: list[tuple[int, int]] = field(
        default_factory=lambda: [
            (0, 0),
            (1, 0),
            (1, 1),
            (2, 1),
            (3, 1),
            (3, 2),
        ]
    )
