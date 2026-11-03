"""Rules and sampling for a single-player snakes and ladders race."""

from dataclasses import dataclass, field
from random import Random
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class Board:
    size: int
    jumps: Mapping[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.size < 2:
            raise ValueError("size must be at least 2")
        jumps = dict(self.jumps)
        for start, end in jumps.items():
            if not 1 <= start < self.size:
                raise ValueError(f"jump start {start} is outside the board")
            if not 0 <= end < self.size or start == end:
                raise ValueError(f"invalid jump from {start} to {end}")
        object.__setattr__(self, "jumps", MappingProxyType(jumps))

    def advance(self, position: int, roll: int) -> int:
        """Move once, then follow at most one snake or ladder."""
        if not 0 <= position < self.size or not 1 <= roll <= 6:
            raise ValueError("invalid position or die roll")
        landing = position + roll
        if landing >= self.size:
            return self.size
        return self.jumps.get(landing, landing)


def play_game(board: Board, rng: Random, max_rolls: int = 10_000) -> int:
    """Return rolls to finish; fail explicitly if the limit is reached."""
    if max_rolls < 1:
        raise ValueError("max_rolls must be positive")
    position = 0
    for turn in range(1, max_rolls + 1):
        position = board.advance(position, rng.randint(1, 6))
        if position == board.size:
            return turn
    raise RuntimeError(f"game did not finish in {max_rolls} rolls")


def sample_games(
    board: Board, count: int, seed: int = 0, max_rolls: int = 10_000
) -> list[int]:
    """Sample independent games from one reproducible die stream."""
    if count < 1:
        raise ValueError("count must be positive")
    rng = Random(seed)
    return [play_game(board, rng, max_rolls) for _ in range(count)]
