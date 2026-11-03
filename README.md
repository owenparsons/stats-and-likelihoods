# Snakes and ladders experiments

A small Python project for studying how board layout changes the distribution of rolls to finish. It uses only the standard library.

The starting square is `0`. A board is defined by its final square and a mapping from landing squares to destinations: a larger destination is a ladder, and a smaller one is a snake. Each turn rolls a fair six-sided die. Reaching or passing the final square wins; a snake or ladder is applied only after landing on a square, and at most once per turn.

The first experiments compare completion times for an empty board and boards with one ladder or one snake. They measure the shape of the completion-time distribution, rather than fairness between players. We can define a particular notion of fairness before searching for boards that optimize it.

Run the comparisons with `python3 experiments.py`. Use `--games 50000 --seed 42` to set the sample size and seed, `--bin-width 1` for individual roll counts, or `--csv results.csv` to save every result for later analysis. Run the rule tests with `python3 -m unittest discover -s tests`.

Edit `BOARDS` in `experiments.py` to try another layout. The summary uses population standard deviation, moment skewness, and excess kurtosis; histograms group rolls in bins of two by default. Every game has a 10,000-roll safety limit, which raises an error rather than silently dropping a long game.
