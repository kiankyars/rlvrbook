# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.11.2", "numpy"]
# ///
"""Generate the Chapter 7 over-optimization curve figure.

Writes book/diagrams/07-overoptimization-curve-{light,dark}.svg.

Run from the repository root:

    uv run scripts/figures/07-overoptimization-curve.py

The curves use the RL functional form of Gao, Schulman and Hilton (2023,
arXiv:2210.10760, Section 1, p. 2). With d = sqrt(KL(pi || pi_init)) the gold
reward model score after RL against a proxy reward model is

    R_RL(d) = d (alpha_RL - beta_RL log d),        R(0) := 0,

so the gold score peaks at d* = exp(alpha_RL / beta_RL - 1), that is at
KL* = d*^2, where it equals beta_RL d*. The paper's best-of-n form,
R_bon(d) = d (alpha_bon - beta_bon d), is not drawn here. The proxy score is
drawn with the same form and a much smaller beta: the paper could not fit the
proxy scores satisfactorily (Section 3.1), reports that when modelled with the
gold functional forms the proxy fits have much lower values of beta_bon
(Section 3.2), and treats the proxy score as roughly linear in sqrt(KL) for
both RL and best-of-n (Sections 3.2 and 4.2).

The coefficients are illustrative, chosen to match the trends the paper
reports rather than taken from a table (the paper tabulates none):

- Section 3.2 and footnote 2 (p. 2) hold alpha_RL constant across reward-model
  sizes. alpha_RL = 0.38 is inferred from the fitted gold peaks in Figure 1b
  (RM sizes 3M-3B, 1.2B policy, 6B gold RM, x axis on a square-root scale):
  a 3B proxy RM peaks near 1.08 at KL ~ 80 nats and a 12M proxy RM near 0.6
  at KL ~ 15 nats.
- beta_RL for the gold score is read from Figure 3c (Section 3.2), which plots
  the fitted beta_RL against RM parameter count on a log axis with a roughly
  linear (logarithmic) trend from about 0.175 at 3M to about 0.12 at 3B:
  12M ~ 0.167, 300M ~ 0.124, 3B ~ 0.118.
- beta for the proxy score is set so that the 12M proxy reaches about 1.5 at
  KL = 100 nats and the 3B proxy reaches it near KL = 40 nats, as in Figure 1b.

The three reward-model sizes are three of the nine the paper trains. The
resulting picture is the one Figure 1b shows: the proxy score climbs
monotonically, the gold score rises and then falls, and a larger proxy reward
model peaks later and higher.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "book" / "diagrams"
STEM = "07-overoptimization-curve"

# alpha_RL is held constant across reward-model sizes (Gao et al., Section 3.2).
ALPHA_RL = 0.38
# name: (legend label, gold beta_RL, proxy beta_RL, color key)
REWARD_MODELS = [
    ("12M proxy RM", 0.167, 0.100, "small"),
    ("300M proxy RM", 0.124, 0.089, "mid"),
    ("3B proxy RM", 0.118, 0.078, "large"),
]

# Palette shared with the other light/dark figures.
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#111827",
        "small": "#6b7280",
        "mid": "#1d4ed8",
        "large": "#c2410c",
    },
    "dark": {
        "bg": "#0b0f14",
        "fg": "#e5e7eb",
        "small": "#9ca3af",
        "mid": "#93c5fd",
        "large": "#fb923c",
    },
}

KL_MAX = 100.0
Y_MAX = 1.8
PROXY_DASHES = (0, (4.5, 2.5))


def r_rl(d, alpha, beta):
    """Gao et al. RL form, with R(0) := 0."""
    d = np.asarray(d, dtype=float)
    out = np.zeros_like(d)
    pos = d > 0
    out[pos] = d[pos] * (alpha - beta * np.log(d[pos]))
    return out


def peak(alpha, beta):
    """(KL*, R*) at which the RL form is maximal."""
    d_star = np.exp(alpha / beta - 1.0)
    return d_star**2, beta * d_star


def nats(x, _pos):
    return f"{int(round(x))}"


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

    fig, ax = plt.subplots(figsize=(8.2, 4.5), layout="constrained")
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["bg"])

    # Sample uniformly in d = sqrt(KL) so the curves are smooth near the origin
    # on the square-root axis.
    d = np.linspace(0.0, np.sqrt(KL_MAX), 600)
    kl = d**2

    handles = []
    for label, beta_gold, beta_proxy, key in REWARD_MODELS:
        ax.plot(
            kl,
            r_rl(d, ALPHA_RL, beta_proxy),
            color=t[key],
            lw=1.8,
            ls=PROXY_DASHES,
            zorder=2,
        )
        (line,) = ax.plot(kl, r_rl(d, ALPHA_RL, beta_gold), color=t[key], lw=2.2, label=label, zorder=3)
        handles.append(line)
        kl_star, r_star = peak(ALPHA_RL, beta_gold)
        ax.plot(
            [kl_star],
            [r_star],
            marker="o",
            ms=6,
            mfc=t[key],
            mec=t["bg"],
            mew=1.2,
            ls="none",
            zorder=4,
        )

    style_handles = [
        Line2D([], [], color=t["fg"], lw=2.2, label="gold reward (solid)"),
        Line2D([], [], color=t["fg"], lw=1.8, ls=PROXY_DASHES, label="proxy reward (dashed)"),
        Line2D(
            [],
            [],
            color=t["fg"],
            marker="o",
            ms=6,
            mec=t["bg"],
            mew=1.2,
            ls="none",
            label="peak gold reward",
        ),
    ]

    # Square-root x axis, as in Gao et al., Figure 1.
    ax.set_xscale("function", functions=(np.sqrt, np.square))
    ax.set_xlim(0.0, KL_MAX)
    ax.set_ylim(0.0, Y_MAX)
    ax.xaxis.set_major_locator(FixedLocator([0, 5, 10, 20, 40, 60, 80, 100]))
    ax.xaxis.set_major_formatter(FuncFormatter(nats))
    ax.xaxis.set_minor_locator(FixedLocator([1, 2, 3, 4, 15, 30, 50, 70, 90]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which="both", colors=t["fg"])
    ax.set_xlabel("KL divergence from the initial policy (nats, square-root scale)")
    ax.set_ylabel("reward model score")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # Interleave so that the first legend row holds the reward-model sizes and
    # the second row holds the line styles (legend entries fill column-major).
    ordered = []
    for size_handle, style_handle in zip(handles, style_handles):
        ordered.extend([size_handle, style_handle])
    legend = fig.legend(
        handles=ordered,
        loc="outside lower center",
        ncol=3,
        frameon=False,
        fontsize=9,
        handlelength=2.6,
        columnspacing=2.0,
        labelcolor=t["fg"],
    )
    legend.set_zorder(5)

    out = OUT / f"{STEM}-{theme_name}.svg"
    fig.savefig(out, format="svg", facecolor=t["bg"], metadata={"Date": None})
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    for label, beta_gold, _beta_proxy, _key in REWARD_MODELS:
        kl_star, r_star = peak(ALPHA_RL, beta_gold)
        print(f"{label}: gold peak {r_star:.2f} at KL = {kl_star:.1f} nats")
    for theme_name in THEMES:
        draw(theme_name)


if __name__ == "__main__":
    main()
