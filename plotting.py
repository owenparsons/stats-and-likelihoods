"""Save an SVG comparison of sampled game lengths."""

from collections import Counter
from math import ceil
from pathlib import Path
from typing import Mapping, Sequence
from xml.sax.saxutils import escape


COLORS = ("#334155", "#0f766e", "#c2410c", "#7c3aed")


def save_distribution_plot(
    samples: Mapping[str, Sequence[int]], path: str | Path, subtitle: str = ""
) -> Path:
    """Plot finish frequencies and the chance of still playing after each roll."""
    if not samples or any(not values for values in samples.values()):
        raise ValueError("each board needs at least one sampled game")

    output = Path(path)
    if output.suffix.lower() != ".svg":
        raise ValueError("plot path must end in .svg")

    counts = {name: Counter(values) for name, values in samples.items()}
    limit = max(
        40,
        *(ceil(sorted(values)[ceil(0.99 * len(values)) - 1] / 5) * 5
          for values in samples.values()),
    )
    frequencies = {
        name: [count[roll] / len(samples[name]) for roll in range(limit + 1)]
        for name, count in counts.items()
    }
    remaining = {}
    for name, count in counts.items():
        finished = 0
        remaining[name] = []
        for roll in range(limit + 1):
            finished += count[roll]
            remaining[name].append(1 - finished / len(samples[name]))

    left, right = 100, 1060
    top_a, bottom_a = 190, 390
    top_b, bottom_b = 490, 690
    peak = max(0.1, ceil(max(max(series) for series in frequencies.values()) * 10) / 10)

    def x(roll: int) -> float:
        return left + (right - left) * roll / limit

    def y(value: float, top: int, bottom: int, ceiling: float) -> float:
        return bottom - (bottom - top) * value / ceiling

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 790" '
        'role="img" aria-label="Distribution of rolls to finish">',
        '<rect width="1120" height="790" fill="#fafaf9"/>',
        '<text x="70" y="62" class="title">Rolls to finish</text>',
        f'<text x="70" y="90" class="subtitle">{escape(subtitle)}</text>',
        '<text x="70" y="169" class="panel-title">Share finishing on each roll</text>',
        '<text x="70" y="469" class="panel-title">Chance of still playing after each roll</text>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#1e293b}'
        '.title{font-size:32px;font-weight:700}.subtitle{font-size:15px;fill:#64748b}'
        '.panel-title{font-size:18px;font-weight:700}.tick{font-size:13px;fill:#64748b}'
        '.legend{font-size:15px;font-weight:600}</style>',
    ]

    for index, name in enumerate(samples):
        color = COLORS[index % len(COLORS)]
        legend_x = 70 + index * 340
        svg.append(f'<line x1="{legend_x}" y1="125" x2="{legend_x + 26}" y2="125" '
                   f'stroke="{color}" stroke-width="4"/>')
        svg.append(f'<text x="{legend_x + 35}" y="130" class="legend">{escape(name)}</text>')

    for top, bottom, ceiling, ticks in (
        (top_a, bottom_a, peak, [i / 10 for i in range(round(peak * 10) + 1)]),
        (top_b, bottom_b, 1.0, [i / 4 for i in range(5)]),
    ):
        for tick in ticks:
            tick_y = y(tick, top, bottom, ceiling)
            svg.append(f'<line x1="{left}" y1="{tick_y:.1f}" x2="{right}" '
                       f'y2="{tick_y:.1f}" stroke="#e2e8f0"/>')
            svg.append(f'<text x="{left - 12}" y="{tick_y + 5:.1f}" '
                       f'text-anchor="end" class="tick">{tick:.0%}</text>')
        for roll in range(0, limit + 1, 5):
            tick_x = x(roll)
            svg.append(f'<line x1="{tick_x:.1f}" y1="{bottom}" x2="{tick_x:.1f}" '
                       f'y2="{bottom + 6}" stroke="#94a3b8"/>')
            svg.append(f'<text x="{tick_x:.1f}" y="{bottom + 25}" '
                       f'text-anchor="middle" class="tick">{roll}</text>')

    for index, name in enumerate(samples):
        color = COLORS[index % len(COLORS)]
        points = " ".join(
            f"{x(roll):.1f},{y(value, top_a, bottom_a, peak):.1f}"
            for roll, value in enumerate(frequencies[name])
        )
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" '
                   'stroke-width="2.8" stroke-linejoin="round"/>')
        for roll, value in enumerate(frequencies[name]):
            if value >= 0.005:
                svg.append(f'<circle cx="{x(roll):.1f}" '
                           f'cy="{y(value, top_a, bottom_a, peak):.1f}" r="2.5" '
                           f'fill="{color}"/>')

        series = remaining[name]
        steps = [f"M{x(0):.1f},{y(series[0], top_b, bottom_b, 1):.1f}"]
        for roll in range(1, limit + 1):
            steps.append(f"H{x(roll):.1f}V{y(series[roll], top_b, bottom_b, 1):.1f}")
        svg.append(f'<path d="{" ".join(steps)}" fill="none" stroke="{color}" '
                   'stroke-width="2.8" stroke-linejoin="round"/>')

    svg.append('<text x="580" y="750" text-anchor="middle" class="tick">Rolls</text>')
    svg.append(f'<text x="1060" y="777" text-anchor="end" class="tick">'
               f'Games beyond {limit} rolls appear in the lower chart at {limit}.</text>')
    svg.append("</svg>")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(svg), encoding="utf-8")
    return output
