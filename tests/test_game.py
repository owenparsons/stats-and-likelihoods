import unittest

from game import Board, play_game, sample_games


class FixedDie:
    def __init__(self, rolls):
        self.rolls = iter(rolls)

    def randint(self, low, high):
        return next(self.rolls)


class GameTests(unittest.TestCase):
    def test_ladder_and_snake_apply_once(self):
        board = Board(20, {3: 14, 14: 2})
        self.assertEqual(board.advance(0, 3), 14)
        self.assertEqual(board.advance(13, 1), 2)

    def test_overshoot_wins(self):
        self.assertEqual(play_game(Board(10), FixedDie([6, 6])), 2)

    def test_roll_limit_raises(self):
        with self.assertRaises(RuntimeError):
            play_game(Board(20), FixedDie([1, 1]), max_rolls=2)

    def test_sampling_is_reproducible(self):
        board = Board(30, {3: 20})
        self.assertEqual(sample_games(board, 100, seed=42), sample_games(board, 100, seed=42))

    def test_invalid_jump_is_rejected(self):
        with self.assertRaises(ValueError):
            Board(20, {20: 2})


if __name__ == "__main__":
    unittest.main()
