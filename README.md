# Snakes and ladders experiments

A small Python project for studying how board layout changes the distribution of rolls to finish. It uses only the standard library.

The starting square is `0`. A board is defined by its final square and a mapping from landing squares to destinations: a larger destination is a ladder, and a smaller one is a snake. Each turn rolls a fair six-sided die. Reaching or passing the final square wins; a snake or ladder is applied only after landing on a square, and at most once per turn.

The first experiments compare completion times for an empty board and boards with one ladder or one snake. They measure the shape of the completion-time distribution, rather than fairness between players. We can define a particular notion of fairness before searching for boards that optimize it.
