# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.11.2", "numpy"]
# ///
"""Generate the Chapter 11 ScaleRL ceiling-versus-efficiency figure.

Writes book/diagrams/11-scalerl-ceiling-vs-efficiency-{light,dark}.svg.

Run from the repository root:

    uv run code/figures/11-scalerl-ceiling-vs-efficiency.py

The curves use the sigmoid of ScaleRL (Khatri et al., 2025, arXiv:2510.13786,
Eq. 1, p. 2):

    R_C = R_0 + (A - R_0) / (1 + (C_mid / C)^B)

A is the ceiling (asymptotic pass rate), C_mid the compute at which half the
gain is made, and B the steepness. The parameters are illustrative, not fitted
to a run. They are chosen to show the lesson of ScaleRL's Figure 13b
(Appendix A.8) and of its generation-length and batch-size results (Section 4,
Figures 9 and 10): a recipe that only reaches the same ceiling sooner leads
early, while a recipe that raises the ceiling can trail early and overtake only
at larger compute. B is held equal across the three curves so that each pair
crosses at most once.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "book" / "diagrams"
STEM = "11-scalerl-ceiling-vs-efficiency"

R0 = 0.10
# name: (legend label, A, C_mid, B, color key, line width)
RECIPES = [
    ("baseline recipe", 0.50, 3000.0, 1.5, "base", 2.0),
    ("same ceiling, reached sooner (smaller $C_{mid}$)", 0.50, 1000.0, 1.5, "eff", 2.4),
    ("higher ceiling $A$, slower start (larger $C_{mid}$)", 0.62, 6000.0, 1.5, "ceil", 2.4),
]

# Palette shared with the other Chapter 11 light/dark figures.
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#111827",
        "base": "#6b7280",
        "eff": "#1d4ed8",
        "ceil": "#c2410c",
    },
    "dark": {
        "bg": "#0b0f14",
        "fg": "#e5e7eb",
        "base": "#9ca3af",
        "eff": "#93c5fd",
        "ceil": "#fb923c",
    },
}

C_MIN, C_MAX = 1e2, 2e5


def sigmoid(c, a, c_mid, b):
    return R0 + (a - R0) / (1.0 + (c_mid / c) ** b)


def thousands(x, _pos):
    return f"{int(round(x)):,}"


def draw(theme_name):
    t = THEMES[theme_name]
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "svg.fonttype": "path",
            "svg.hashsalt": STEM,
            "text.color": t["fg"],
            "axes.labelcolor": t["fg"],
            "axes.edgecolor": t["fg"],
            "xtick.color": t["fg"],
            "ytick.color": t["fg"],
        }
    )

    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["bg"])

    c = np.logspace(np.log10(C_MIN), np.log10(C_MAX), 600)

    # Ceilings: one dotted line per distinct A, in the color of the recipe
    # that owns it (baseline gray for the shared A = 0.50).
    ceilings = {}
    for _label, a, _c_mid, _b, key, _lw in RECIPES:
        ceilings.setdefault(a, key)
    for a, key in ceilings.items():
        ax.axhline(a, color=t[key], lw=1.2, ls=(0, (1, 2)), zorder=1)

    handles = []
    for label, a, c_mid, b, key, lw in RECIPES:
        (line,) = ax.plot(c, sigmoid(c, a, c_mid, b), color=t[key], lw=lw, label=label, zorder=3)
        handles.append(line)
        # Half the gain is made at C = C_mid.
        ax.plot(
            [c_mid],
            [R0 + (a - R0) / 2],
            marker="o",
            ms=6,
            mfc=t[key],
            mec=t["bg"],
            mew=1.2,
            ls="none",
            zorder=4,
        )

    handles.append(Line2D([], [], color=t["fg"], lw=1.2, ls=(0, (1, 2)), label="ceiling $A$"))
    handles.append(
        Line2D(
            [],
            [],
            color=t["fg"],
            marker="o",
            ms=6,
            mec=t["bg"],
            mew=1.2,
            ls="none",
            label="$C_{mid}$: half the gain made",
        )
    )

    ax.set_xscale("log")
    ax.set_xlim(C_MIN, C_MAX)
    ax.set_ylim(0.05, 0.70)
    ax.xaxis.set_major_locator(FixedLocator([1e2, 1e3, 1e4, 1e5]))
    ax.xaxis.set_major_formatter(FuncFormatter(thousands))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which="both", colors=t["fg"])
    ax.set_xlabel("RL training compute (GPU-hours, log scale)")
    ax.set_ylabel("held-out pass rate")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    legend = ax.legend(
        handles=handles,
        loc="lower right",
        frameon=False,
        fontsize=9,
        handlelength=2.6,
        labelcolor=t["fg"],
    )
    legend.set_zorder(5)

    fig.tight_layout()
    out = OUT / f"{STEM}-{theme_name}.svg"
    fig.savefig(out, format="svg", facecolor=t["bg"], metadata={"Date": None})
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    for theme_name in THEMES:
        draw(theme_name)


if __name__ == "__main__":
    main()
