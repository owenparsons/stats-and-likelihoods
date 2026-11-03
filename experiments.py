"""Compare completion-time distributions for a few small boards."""

import argparse
import csv
from collections import Counter
from math import ceil, sqrt
from statistics import fmean, median

from game import Board, sample_games


BOARDS = {
    "empty": Board(30),
    "early ladder (3→20)": Board(30, {3: 20}),
    "late snake (25→5)": Board(30, {25: 5}),
}


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[ceil(fraction * len(ordered)) - 1]


def describe(values: list[int]) -> dict[str, float]:
    mean = fmean(values)
    m2 = fmean((value - mean) ** 2 for value in values)
    m3 = fmean((value - mean) ** 3 for value in values)
    m4 = fmean((value - mean) ** 4 for value in values)
    return {
        "mean": mean,
        "median": median(values),
        "sd": sqrt(m2),
        "p90": percentile(values, 0.9),
        "skew": m3 / m2**1.5 if m2 else 0.0,
        "excess_kurtosis": m4 / m2**2 - 3 if m2 else 0.0,
    }


def histogram(values: list[int], width: int = 2) -> str:
    """Show bins through p99, with a final tail bin."""
    upper = max(20, ceil(percentile(values, 0.99) / width) * width)
    counts = Counter(min((value - 1) // width, upper // width) for value in values)
    peak = max(counts.values())
    lines = []
    for bucket in range(upper // width + 1):
        label = f"{bucket * width + 1:>3}–{(bucket + 1) * width:<3}"
        if bucket == upper // width:
            label = f"{upper + 1:>3}+   "
        count = counts[bucket]
        bar = "█" * round(30 * count / peak)
        lines.append(f"  {label} {count / len(values):6.1%} {bar}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=50_000, help="games per board")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--bin-width", type=int, default=2)
    parser.add_argument("--csv", help="optional path for raw roll counts")
    args = parser.parse_args()
    if args.games < 1:
        parser.error("--games must be positive")
    if args.bin_width < 1:
        parser.error("--bin-width must be positive")

    samples = {name: sample_games(board, args.games, args.seed) for name, board in BOARDS.items()}
    print(f"{args.games:,} games per board; seed {args.seed}; finish on reach or pass\n")
    print(f"{'board':<24} {'mean':>7} {'median':>7} {'sd':>7} {'p90':>5} {'skew':>7} {'excess kurt.':>12}")
    for name, values in samples.items():
        stats = describe(values)
        print(
            f"{name:<24} {stats['mean']:7.2f} {stats['median']:7.1f} "
            f"{stats['sd']:7.2f} {stats['p90']:5.0f} {stats['skew']:7.2f} "
            f"{stats['excess_kurtosis']:12.2f}"
        )
    for name, values in samples.items():
        print(f"\n{name}\n{histogram(values, args.bin_width)}")

    if args.csv:
        with open(args.csv, "w", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(["board", "rolls_to_win"])
            for name, values in samples.items():
                writer.writerows((name, value) for value in values)


if __name__ == "__main__":
    main()
