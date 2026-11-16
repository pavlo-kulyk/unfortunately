#!/usr/bin/env python3
"""UNFORTUNATELY — funnel chart (imported by charts_report.py)
Reads ../unfortunately_dataset.csv, writes PNG + SVG into ../charts/.
Run:  python3 funnel.py
"""
from __future__ import annotations

from pathlib import Path
from load_data import load, OUT


import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Polygon


PINK_PALE = "#f8c7d8"
PINK_LITE = "#f0a0be"
PINK_MID = "#e45e8e"
PINK_DARK = "#d44e80"
PINK = "#d81b60"
INK = "#1a1a1a"
MUTE = "#555555"
GRID = "#aaaaaa"
WHITE = "#ffffff"
AXIS_Y = -1.12
TICK_BOTTOM = -1.17


def _yes(records: pd.DataFrame, column: str) -> int:
    return int(records[column].astype(str).str.strip().str.upper().eq("YES").sum())


def _format_pct(pct: float) -> tuple[str, int]:
    if pct >= 50:
        return f"{pct:.0f}%", 18
    if pct >= 10:
        return f"{pct:.0f}%", 15
    if pct >= 5:
        return f"{pct:.1f}%", 14
    return f"{pct:.1f}%", 13


def render_funnel() -> None:
    records = load()

    sent = len(records)
    delivered = _yes(records, "Delivered")
    any_reply = _yes(records, "Is there an answer")
    human = _yes(records, "Human reply (YES) or automatic reply (NO)")
    positive = _yes(records, "Positive feedback on my technique")

    stages = [
        ("sent", sent, PINK_PALE),
        ("delivered", delivered, PINK_LITE),
        ("replies", any_reply, PINK_MID),
        ("human\nreplies", human, PINK_DARK),
        ("positive\nfeedback", positive, PINK),
    ]
    heights = [value / sent for _, value, _ in stages]

    with mpl.rc_context({
        "font.family": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "savefig.dpi": 150,
        "svg.fonttype": "none",
    }):
        fig = plt.figure(figsize=(8.0, 5.5))

        ax_t = fig.add_axes([0.04, 0.86, 0.92, 0.10])
        ax_t.axis("off")
        ax_t.text(0, 0.95, "Cold email funnel",
                  fontsize=18, fontweight="bold", color=INK, va="top", ha="left")
        ax_t.text(0, 0.18, f"{sent:,} art institutions",
                  fontsize=11, color=MUTE, va="top", ha="left", fontstyle="italic")

        ax = fig.add_axes([0.04, 0.13, 0.92, 0.70])
        ax.set_xlim(0, len(stages))
        ax.set_ylim(-1.16, 1.05)
        ax.axis("off")

        for i in range(len(stages) - 1):
            h_left = heights[i]
            h_right = heights[i + 1]
            color = stages[i + 1][2]
            poly = Polygon([
                (i, +h_left),
                (i + 1, +h_right),
                (i + 1, -h_right),
                (i, -h_left),
            ], facecolor=color, edgecolor=WHITE, linewidth=1.8, joinstyle="miter")
            ax.add_patch(poly)

        band_pcts = [heights[i + 1] * 100 for i in range(len(stages) - 1)]
        band_centers_x = [i + 0.5 for i in range(len(stages) - 1)]
        float_threshold = 0.04
        for i, (pct, x) in enumerate(zip(band_pcts, band_centers_x)):
            h_right = heights[i + 1]
            label, fontsize = _format_pct(pct)
            if h_right >= float_threshold:
                ax.text(x, 0, label, ha="center", va="center",
                        fontsize=fontsize, fontweight="bold", color=WHITE)
            else:
                x_tip = i + 1
                x_label = len(stages) - 1 + 0.06
                ax.plot([x_tip, x_label - 0.015], [0, 0],
                        color=GRID, linewidth=0.7)
                ax.text(x_label, 0, label, ha="left", va="center",
                        fontsize=fontsize, fontweight="bold", color=PINK)

        ax.plot([0, len(stages) - 1], [AXIS_Y, AXIS_Y],
                color=GRID, linewidth=0.8, clip_on=False)
        for i in range(len(stages)):
            ax.plot([i, i], [AXIS_Y, TICK_BOTTOM], color=GRID, linewidth=0.8, clip_on=False)

        ax_l = fig.add_axes([0.04, 0.02, 0.92, 0.10])
        ax_l.axis("off")
        ax_l.set_xlim(0, len(stages))
        ax_l.set_ylim(0, 1)
        for i, (label, value, _) in enumerate(stages):
            ax_l.text(i, 0.88, f"{value:,}", ha="center", va="top",
                      fontsize=12.5, fontweight="bold", color=INK)
            ax_l.text(i, 0.36, label, ha="center", va="top",
                      fontsize=10, color=MUTE)

        fig.savefig(OUT / "01_funnel.svg", bbox_inches="tight", facecolor=WHITE)
        fig.savefig(OUT / "01_funnel.png", dpi=150, bbox_inches="tight", facecolor=WHITE)
        plt.close(fig)

    print("Regenerated article/web/01_funnel.svg and .png")


if __name__ == "__main__":
    render_funnel()
