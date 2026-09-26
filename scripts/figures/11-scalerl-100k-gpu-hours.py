# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.11.2", "numpy", "scipy", "pillow"]
# ///
"""Generate the Chapter 11 ScaleRL 100k GPU-hours figure.

Writes book/diagrams/11-scalerl-100k-gpu-hours-{light,dark}.svg.

Run from the repository root:

    uv run scripts/figures/11-scalerl-100k-gpu-hours.py

This redraws Figure 1 of ScaleRL (Khatri et al., 2025, arXiv:2510.13786,
CC BY 4.0), "Validation perf., Scaling RL Compute", so that the legend sits
below the axes instead of over the curves. The plotted points were digitized
from the paper's Figure 1 (the PNG in book/diagrams/) by detecting the marker
colors and mapping pixel positions to data through the axis ticks, so they are
approximate: about one pixel, or 0.001 in pass rate and 1% in compute. Markers
that overlap in the paper cannot always be separated, so a few of its points
are missing here.

Each run's sigmoid (ScaleRL Eq. 1, p. 2) is fitted to its training points by
least squares and drawn solid over the training range and dotted beyond it:

    R_C = R_0 + (A - R_0) / (1 + (C_mid / C)^B)

Fitted to the digitized training points, the parameters are about
R_0 = 0.396, A = 0.634, C_mid = 9.9k GPU-hours, B = 1.78 for the 8B dense run
and R_0 = 0.510, A = 0.701, C_mid = 6.4k, B = 1.73 for the 17Bx16 MoE run.
The paper's own drawn curves correspond to A = 0.645 (dense) and A = 0.710
(MoE), so these refitted extrapolations run about 0.01 below the paper's at
100k GPU-hours, and the extended points sit slightly above them. The tail of
the sigmoid is that sensitive to sub-pixel errors in the late training points.
Set CURVES = "paper" to draw the paper's curves instead (parameters recovered
by fitting the sigmoid to the paper's drawn solid lines).

Running with --digitize re-extracts the points from the PNG and prints them in
the format of the DATA block, together with the parameters recovered from the
paper's drawn curves. Its pixel windows are specific to that PNG.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "book" / "diagrams"
STEM = "11-scalerl-100k-gpu-hours"
SOURCE_PNG = OUT / "11-scalerl-100k-gpu-hours.png"

# "fit": sigmoid fitted to the digitized training points (default).
# "paper": the sigmoid parameters recovered from the paper's drawn curves.
CURVES = "paper"

# DATA: (compute in thousands of GPU-hours, held-out pass rate), digitized from
# Figure 1 of Khatri et al. (2025). Approximate; see the module docstring.
DENSE_TRAIN = [
    (1.328, 0.4021), (2.670, 0.4203), (3.998, 0.4340), (5.329, 0.4537), (6.680, 0.4737),
    (7.980, 0.4863), (9.341, 0.5049), (10.638, 0.5286), (11.950, 0.5397), (13.333, 0.5503),
    (14.674, 0.5572), (15.930, 0.5595), (17.293, 0.5690), (18.645, 0.5705), (19.966, 0.5785),
    (21.234, 0.5834), (25.369, 0.5940), (26.614, 0.5956), (29.290, 0.6006), (30.728, 0.6056),
    (32.016, 0.6023), (34.519, 0.6133), (37.218, 0.6158), (39.854, 0.6201),
]
DENSE_EXT = [
    (49.272, 0.6270), (50.640, 0.6253), (53.125, 0.6314), (56.114, 0.6314), (60.089, 0.6314),
    (69.376, 0.6358), (73.280, 0.6465), (74.800, 0.6402), (78.470, 0.6447), (89.367, 0.6402),
]
MOE_TRAIN = [
    (1.241, 0.5177), (1.870, 0.5337), (2.493, 0.5420), (3.104, 0.5549), (3.734, 0.5627),
    (4.340, 0.5705), (4.977, 0.5769), (5.591, 0.5923), (6.195, 0.6082), (6.818, 0.6133),
    (7.453, 0.6236), (8.090, 0.6227), (9.341, 0.6367), (9.934, 0.6402), (11.160, 0.6411),
    (11.788, 0.6519), (12.451, 0.6546), (13.062, 0.6555), (14.278, 0.6601), (14.876, 0.6684),
    (15.500, 0.6693),
]
MOE_EXT = [
    (18.645, 0.6806), (19.830, 0.6768), (23.052, 0.6891), (25.544, 0.6968), (26.797, 0.7007),
    (27.920, 0.6949), (34.756, 0.7095), (38.250, 0.7056), (41.241, 0.7056), (42.970, 0.7115),
    (44.162, 0.6959),
]

# (R_0, A, C_mid in thousands of GPU-hours, B) recovered from the paper's drawn
# solid curves; they reproduce its dotted extrapolations to within 0.003.
PAPER_PARAMS = {
    "dense": (0.4017, 0.6446, 10.92, 1.682),
    "moe": (0.5116, 0.7099, 6.92, 1.659),
}

RUNS = [
    # key, legend name, training points, extended points, color key
    ("dense", "8B dense", DENSE_TRAIN, DENSE_EXT, "eff"),
    ("moe", "17Bx16 MoE", MOE_TRAIN, MOE_EXT, "ceil"),
]

# Palette shared with the other Chapter 11 light/dark figures.
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#111827",
        "eff": "#1d4ed8",
        "ceil": "#c2410c",
    },
    "dark": {
        "bg": "#0b0f14",
        "fg": "#e5e7eb",
        "eff": "#93c5fd",
        "ceil": "#fb923c",
    },
}

C_MIN, C_MAX = 0.9, 180.0  # thousands of GPU-hours, as in the paper's axes
R_MIN, R_MAX = 0.39, 0.765
C_END = 100.0  # the extrapolations run to 100k GPU-hours
X_TICKS = [1, 2, 4, 8, 16, 32, 64, 128]
Y_TICKS = [0.40, 0.44, 0.48, 0.52, 0.56, 0.60, 0.64, 0.68, 0.72, 0.76]


def sigmoid(c, r0, a, c_mid, b):
    return r0 + (a - r0) / (1.0 + (c_mid / c) ** b)


def fit(points):
    c = np.array([p[0] for p in points])
    r = np.array([p[1] for p in points])
    params, _ = curve_fit(
        sigmoid,
        c,
        r,
        p0=[r[0], 0.7, 10.0, 1.0],
        bounds=([0.0, 0.4, 0.1, 0.1], [0.6, 1.0, 1e4, 6.0]),
        maxfev=50000,
    )
    return tuple(float(v) for v in params)


def curve_params(key, train):
    return PAPER_PARAMS[key] if CURVES == "paper" else fit(train)


def draw(theme_name, params):
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

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["bg"])

    dotted = (0, (1.5, 2.5))
    handles = {"train": [], "ext": [], "fit": [], "extrap": []}
    for key, name, train, ext, color_key in RUNS:
        color = t[color_key]
        r0, a, c_mid, b = params[key]
        c_lo = min(p[0] for p in train)
        c_hi = max(p[0] for p in train)
        c_fit = np.logspace(np.log10(c_lo), np.log10(c_hi), 300)
        c_ext = np.logspace(np.log10(c_hi), np.log10(C_END), 300)
        ax.plot(c_fit, sigmoid(c_fit, r0, a, c_mid, b), color=color, lw=2.0, zorder=3)
        ax.plot(c_ext, sigmoid(c_ext, r0, a, c_mid, b), color=color, lw=2.0, ls=dotted, zorder=3)
        ax.plot(
            [p[0] for p in train],
            [p[1] for p in train],
            marker="*",
            ms=9,
            mfc=color,
            mec="none",
            alpha=0.7,
            ls="none",
            zorder=4,
        )
        ax.plot(
            [p[0] for p in ext],
            [p[1] for p in ext],
            marker="x",
            ms=6,
            mec=color,
            mew=1.4,
            ls="none",
            zorder=4,
        )
        handles["train"].append(
            Line2D([], [], marker="*", ms=9, mfc=color, mec="none", alpha=0.7, ls="none", label=f"{name}: training points")
        )
        handles["ext"].append(Line2D([], [], marker="x", ms=6, mec=color, mew=1.4, ls="none", label="extended points"))
        handles["fit"].append(Line2D([], [], color=color, lw=2.0, label="fitted curve"))
        handles["extrap"].append(Line2D([], [], color=color, lw=2.0, ls=dotted, label="extrapolation"))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(C_MIN, C_MAX)
    ax.set_ylim(R_MIN, R_MAX)
    ax.xaxis.set_major_locator(FixedLocator(X_TICKS))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{int(round(x))}"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator(Y_TICKS))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _pos: f"{y:.2f}"))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which="both", colors=t["fg"])
    ax.set_xlabel("RL training compute (thousands of GPU-hours, log scale)")
    ax.set_ylabel("held-out pass rate (log scale)")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # Legend below the axes: one row per run, filled column by column.
    ordered = handles["train"] + handles["ext"] + handles["fit"] + handles["extrap"]
    legend = ax.legend(
        handles=ordered,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=4,
        frameon=False,
        fontsize=9,
        handlelength=2.6,
        columnspacing=1.6,
        labelcolor=t["fg"],
    )
    legend.set_zorder(5)

    fig.tight_layout()
    out = OUT / f"{STEM}-{theme_name}.svg"
    fig.savefig(out, format="svg", facecolor=t["bg"], metadata={"Date": None})
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def digitize():
    """Re-extract the points from the paper's Figure 1 PNG and print them."""
    from PIL import Image, ImageDraw
    from scipy import ndimage

    img = np.asarray(Image.open(SOURCE_PNG).convert("RGB")).astype(int)
    height, width, _ = img.shape
    red, green, blue = img[..., 0], img[..., 1], img[..., 2]
    gray = img.mean(axis=2)

    # Axis calibration from the tick marks: x ticks 1..128 (log2 spacing) below
    # the bottom spine, y ticks 0.40..0.76 (log spacing) left of the left spine.
    def tick_centers(values):
        centers, run = [], [values[0]]
        for v in values[1:]:
            if v - run[-1] <= 1:
                run.append(v)
            else:
                centers.append(np.mean(run))
                run = [v]
        centers.append(np.mean(run))
        return centers

    dark = gray < 160
    x_ticks = tick_centers([i for i in range(width) if dark[526:532, i].sum() >= 3])
    y_ticks = tick_centers([i for i in range(height) if dark[i, 100:110].sum() >= 3])
    px_per_doubling = (x_ticks[-1] - x_ticks[0]) / 7.0
    y_coef = np.polyfit(np.log(Y_TICKS[::-1]), y_ticks, 1)  # row = m * ln(y) + c

    def to_data(px, py):
        return 2 ** ((px - x_ticks[0]) / px_per_doubling), np.exp((py - y_coef[1]) / y_coef[0])

    inside = np.zeros((height, width), bool)
    inside[50:522, 113:885] = True
    legend_box = np.zeros((height, width), bool)  # top-left legend, markers only
    legend_box[55:200, 112:235] = True
    legend_text = np.zeros((height, width), bool)  # top-left legend with its text
    legend_text[55:200, 112:580] = True
    names_box = np.zeros((height, width), bool)  # bottom-right run names
    names_box[415:495, 500:845] = True

    blueish = (blue > red + 18) & (blue > green + 3) & (gray < 248)
    orangeish = (red > blue + 25) & (red > green + 6) & (green > blue + 6) & (gray < 250)
    reddish = (red > 150) & (green < 120) & (blue < 120) & (red - green > 80)
    blackish = img.max(axis=2) < 140
    line_rgb = {"dense": np.array([31, 119, 180]), "moe": np.array([255, 127, 14])}

    def peaks(score, threshold, valid=None):
        local_max = score == ndimage.maximum_filter(score, size=7)
        cand = local_max & (score >= threshold)
        if valid is not None:
            cand &= valid
        labels, n = ndimage.label(cand)
        found = []
        for i in range(1, n + 1):
            ys, xs = np.where(labels == i)
            found.append((xs.mean(), ys.mean(), float(score[ys[0], xs[0]])))
        return found

    def merge(found, radius):
        kept = []
        for p in sorted(found, key=lambda q: -q[2]):
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > radius**2 for q in kept):
                kept.append(p)
        return sorted(kept)

    def star_kernels(outer=7.7, inner_ratio=0.40, ring=2.5):
        size = int(2 * (outer + ring)) + 3
        s = 8
        canvas = Image.new("L", (size * s, size * s), 0)
        c = size * s / 2
        poly = []
        for i in range(10):
            ang = -np.pi / 2 + i * np.pi / 5
            rad = (outer if i % 2 == 0 else outer * inner_ratio) * s
            poly.append((c + rad * np.cos(ang), c + rad * np.sin(ang)))
        ImageDraw.Draw(canvas).polygon(poly, fill=255)
        star = np.asarray(canvas.resize((size, size), Image.BOX)).astype(float) / 255.0 > 0.5
        yy, xx = np.mgrid[0:size, 0:size]
        disk = (xx - size // 2) ** 2 + (yy - size // 2) ** 2 <= (outer + ring) ** 2
        ring_mask = disk & ~ndimage.binary_dilation(star, iterations=1)
        return star.astype(float), ring_mask.astype(float)

    star_k, ring_k = star_kernels()

    def stars(colored, rgb, excluded):
        # The opaque fitted line hides part of every star, so score each
        # candidate centre by the fraction of its visible star area that is lit.
        dist = np.sqrt(((img - rgb) ** 2).sum(axis=2))
        band = ndimage.binary_dilation(dist < 60, iterations=1)
        ok = inside & ~excluded
        lit = (colored & ~band & ok).astype(float)
        avail = (~band & ok).astype(float)
        corr = lambda m, k: ndimage.correlate(m, k, mode="constant")
        score = corr(lit, star_k) / np.maximum(corr(avail, star_k), 1) - 0.7 * corr(lit, ring_k) / np.maximum(
            corr(avail, ring_k), 1
        )
        return merge(peaks(score, 0.55, valid=corr(avail, star_k) >= 10), 5.0)

    def crosses(mask, excluded, size=13):
        k = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                if abs(i - j) <= 1 or abs(i + j - (size - 1)) <= 1:
                    k[i, j] = 1.0
        pos = k.sum()
        k[k == 0] = -0.6 * pos / (size * size - pos)
        score = ndimage.correlate((mask & inside & ~excluded).astype(float), k, mode="constant") / pos
        return merge(peaks(score, 0.5), 4.0)

    def drawn_curve(rgb, col_lo, col_hi):
        # Median row of the opaque line per column, for recovering the paper's fit.
        dist = np.sqrt(((img - rgb) ** 2).sum(axis=2))
        core = dist < 40
        core[:200, :240] = False
        cs, rs = [], []
        for col in range(col_lo, col_hi):
            rows = np.where(core[60:522, col])[0] + 60
            if len(rows) >= 3 and rows.max() - rows.min() < 12:
                c, r = to_data(col, np.median(rows))
                cs.append(c)
                rs.append(r)
        return np.array(cs), np.array(rs)

    found = {
        "DENSE_TRAIN": stars(blueish, line_rgb["dense"], legend_box | names_box),
        "DENSE_EXT": crosses(blackish, legend_text | names_box),
        "MOE_TRAIN": stars(orangeish, line_rgb["moe"], legend_box | names_box),
        "MOE_EXT": crosses(reddish, legend_box | names_box),
    }
    for name, pts in found.items():
        data = [to_data(x, y) for x, y, _ in pts]
        print(f"{name} = [  # {len(data)} points")
        for i in range(0, len(data), 5):
            row = ", ".join(f"({c:.3f}, {r:.4f})" for c, r in data[i : i + 5])
            print(f"    {row},")
        print("]")
    for key, (lo, hi) in {"dense": (185, 655), "moe": (195, 522)}.items():
        cs, rs = drawn_curve(line_rgb[key], lo, hi)
        r0, a, c_mid, b = fit(list(zip(cs, rs)))
        print(f'PAPER_PARAMS["{key}"] = ({r0:.4f}, {a:.4f}, {c_mid:.2f}, {b:.3f})  # from {len(cs)} columns of the drawn line')


def main():
    if "--digitize" in sys.argv[1:]:
        digitize()
        return
    params = {key: curve_params(key, train) for key, _name, train, _ext, _color in RUNS}
    for key, (r0, a, c_mid, b) in params.items():
        print(f"{key}: R_0 = {r0:.4f}, A = {a:.4f}, C_mid = {c_mid:.2f}k GPU-hours, B = {b:.3f}")
    for theme_name in THEMES:
        draw(theme_name, params)


if __name__ == "__main__":
    main()
