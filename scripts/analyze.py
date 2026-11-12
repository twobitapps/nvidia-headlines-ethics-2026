"""Recompute every figure and chart in this repo from data/headlines.csv.

Usage (from the repo root):
    pip install matplotlib pillow
    python scripts/analyze.py

Writes data/summary.json, charts/*.png (dark theme), og-image.png, and the
headline list in README.md.
"""
import csv
import itertools
import json
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "headlines.csv"
CHARTS = ROOT / "charts"

WINDOW_START = date(2026, 5, 11)
WINDOW_END = date(2026, 11, 11)
STORY_BREAK = date(2026, 10, 29)  # NYT: Huang seen as target of Chinese spy plot
MIDTERMS = date(2026, 11, 3)
ADMISSION = date(2026, 11, 8)  # Huang's letter to Nvidia staff acknowledging the affair
EVENTS = [
    (STORY_BREAK, "29 Oct: spy-plot story breaks"),
    (MIDTERMS, "3 Nov: midterms"),
    (ADMISSION, "8 Nov: Huang's letter to staff"),
]
OUTLETS = ["WSJ", "NYT", "The Economist"]

# Two themes. Light sits on GitHub's white page, dark on GitHub's dark page (#0d1117).
# Tone colours: two warm steps for negative, neutral grey for "no ethics content",
# one cool hue for positive. Outlet colours are a separate categorical set
# (validated for colour-vision deficiency in both modes) so they never read as tone.
THEMES = {
    "light": {
        "bg": "#ffffff", "ink": "#1d1f22", "muted": "#62666c", "grid": "#e8e8e4",
        "tone": ["#b3261e", "#e9965a", "#c4c6c9", "#2b7a78"],
        "outlet": {"WSJ": "#2a78d6", "NYT": "#e87ba4", "The Economist": "#6250d6"},
        "rater": ["#3d4451", "#7d838c", "#b9bdc3"],
    },
    "dark": {
        "bg": "#0d1117", "ink": "#e8e9ea", "muted": "#9a9fa6", "grid": "#262a30",
        "tone": ["#e0594f", "#d98a52", "#5b5f66", "#4fb3af"],
        "outlet": {"WSJ": "#3987e5", "NYT": "#d55181", "The Economist": "#9085e9"},
        "rater": ["#e8e9ea", "#a9aeb5", "#6b7078"],
    },
}
CLASS_NAMES = ["Strongly negative", "Mildly negative", "No ethics content", "Defends or praises"]
CLASS_TESTS = [lambda s: s <= -2, lambda s: s == -1, lambda s: s == 0, lambda s: s >= 1]
CHART_THEME = "dark"  # charts are published in the dark theme only; "light" is kept for local use
T = THEMES[CHART_THEME]


def pick_font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"):
        if name in names:
            return name
    return "DejaVu Sans"


FONT = pick_font()


def use_theme(name):
    global T
    T = THEMES[name]
    plt.rcParams.update({
        "font.family": FONT, "font.size": 10.5, "text.color": T["ink"],
        "axes.edgecolor": T["grid"], "axes.labelcolor": T["muted"], "xtick.color": T["muted"],
        "ytick.color": T["muted"], "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": T["bg"], "axes.facecolor": T["bg"], "savefig.facecolor": T["bg"],
        "legend.labelcolor": T["ink"],
    })


def load():
    rows = []
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["date"] = date.fromisoformat(r["date"])
            for k in ("rater_a", "rater_b", "rater_c", "median_score", "about_huang"):
                r[k] = int(r[k])
            rows.append(r)
    return rows


def weighted_kappa(a, b, labels=(-2, -1, 0, 1, 2)):
    k = len(labels)
    n = len(a)
    obs = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[labels.index(x)][labels.index(y)] += 1
    row = [sum(r) for r in obs]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * obs[i][j]
            den += w * row[i] * col[j] / n
    return 1 - num / den if den else 1.0


def stats(rows, key="median_score"):
    n = len(rows)
    if not n:
        return {"n": 0}
    s = [r[key] for r in rows]
    return {
        "n": n,
        "mean_score": round(sum(s) / n, 3),
        "ethics_negative_share": round(sum(x < 0 for x in s) / n, 3),
        "strongly_negative": sum(x <= -2 for x in s),
        "positive": sum(x > 0 for x in s),
    }


PERIODS = {
    "before_story_2026-05-11_to_10-28": lambda r: r["date"] < STORY_BREAK,
    "story_breaks_2026-10-29_to_11-02": lambda r: STORY_BREAK <= r["date"] < MIDTERMS,
    "election_and_after_2026-11-03_to_11-11": lambda r: r["date"] >= MIDTERMS,
    "of_which_2026-11-03_to_11-07": lambda r: MIDTERMS <= r["date"] < ADMISSION,
    "of_which_2026-11-08_to_11-11": lambda r: r["date"] >= ADMISSION,
}


def summarise(rows):
    out = {"headlines": len(rows), "by_outlet": {}, "periods": {}, "per_rater": {},
           "about_huang": {}, "agreement": {}}
    for o in sorted({r["outlet"] for r in rows}):
        out["by_outlet"][o] = {
            "total": sum(r["outlet"] == o for r in rows),
            "before_2026-10-29": stats([r for r in rows if r["outlet"] == o and r["date"] < STORY_BREAK]),
            "from_2026-11-03": stats([r for r in rows if r["outlet"] == o and r["date"] >= MIDTERMS]),
        }
    for name, f in PERIODS.items():
        out["periods"][name] = stats([r for r in rows if f(r)])
        out["about_huang"][name] = stats([r for r in rows if f(r) and r["about_huang"]])
    for k in ("rater_a", "rater_b", "rater_c"):
        out["per_rater"][k] = {name: stats([r for r in rows if f(r)], key=k)
                               for name, f in list(PERIODS.items())[:3]}
    for a, b in itertools.combinations(("rater_a", "rater_b", "rater_c"), 2):
        x, y = [r[a] for r in rows], [r[b] for r in rows]
        out["agreement"][f"{a}_vs_{b}"] = {
            "exact": round(sum(p == q for p, q in zip(x, y)) / len(rows), 3),
            "quadratic_weighted_kappa": round(weighted_kappa(x, y), 3),
        }
    out["agreement"]["all_three_identical"] = sum(
        r["rater_a"] == r["rater_b"] == r["rater_c"] for r in rows)
    out["agreement"]["max_spread"] = max(
        max(r["rater_a"], r["rater_b"], r["rater_c"]) - min(r["rater_a"], r["rater_b"], r["rater_c"])
        for r in rows)
    return out


# ---------- chart helpers ----------

def class_counts(rows):
    return [sum(test(r["median_score"]) for r in rows) for test in CLASS_TESTS]


def weeks():
    return [WINDOW_START + timedelta(days=7 * i) for i in range(27)]


def in_week(r, w):
    return w <= r["date"] < w + timedelta(days=7)


def marker(ax, x, label, y, ha):
    ax.axvline(x, color=T["ink"], lw=1.2, ls=(0, (4, 3)), zorder=3)
    ax.annotate(label, (x, y), xycoords=("data", "axes fraction"), ha=ha, va="bottom",
                fontsize=9.5, fontweight="bold", color=T["ink"],
                xytext=(4 if ha == "left" else -4, 0), textcoords="offset points")


def events(ax, to_x, base=1.03, step=0.09, fontsize=9.5):
    """Mark the three key dates. Later events get higher labels, each right-aligned to its line."""
    from matplotlib.transforms import blended_transform_factory
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for k, (d, label) in enumerate(EVENTS):
        x, y = to_x(d), base + step * k
        ax.axvline(x, color=T["ink"], lw=1.1, ls=(0, (4, 3)), zorder=3)
        ax.plot([x, x], [1, y], transform=tr, clip_on=False, color=T["ink"], lw=1.1, ls=(0, (4, 3)))
        ax.annotate(label, (x, y), xycoords=tr, ha="right", va="bottom", xytext=(-3, 0),
                    textcoords="offset points", fontsize=fontsize, fontweight="bold", color=T["ink"])


def legend(ax, labels, colours, ncol=4, kind="box"):
    if kind == "box":
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colours]
    else:
        handles = [plt.Line2D([0], [0], color=c, lw=2, marker="o", ms=6) for c in colours]
    ax.legend(handles, labels, ncol=ncol, frameon=False, loc="upper left",
              bbox_to_anchor=(0, -0.13), fontsize=9.5, handlelength=1.4, handleheight=1)


def title(ax, text, pad):
    ax.set_title(text, loc="left", fontsize=12.5, fontweight="bold", pad=pad, color=T["ink"])


def grid_y(ax):
    ax.yaxis.grid(True, color=T["grid"], lw=0.8)
    ax.set_axisbelow(True)


def week_ticks(ax):
    ws = weeks()
    ax.set_xticks(range(0, 27, 3), [ws[i].strftime("%-d %b") for i in range(0, 27, 3)])
    ax.set_xlim(-0.7, 26.7)


def week_x(d):
    return (d - WINDOW_START).days / 7 - 0.5


def source_line(rows):
    c = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
    return (f"Source: {c['headlines_listed_total']:,} WSJ, NYT and Economist headlines scanned, 11 May–11 Nov 2026; "
            f"{len(rows)} mention Nvidia or Jensen. Each scored by three independent raters.")


SOURCE = ""


def finish(fig, path):
    """Lay out, add the source line at the foot, save, close."""
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.text(0.012, 0.012, SOURCE, fontsize=8.5, color=T["muted"], ha="left", va="bottom")
    fig.savefig(path)
    plt.close(fig)


# ---------- charts ----------

def weekly_chart(rows, path):
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    for i, w in enumerate(weeks()):
        g = [r for r in rows if in_week(r, w)]
        if not g:
            continue
        bottom = 0.0
        for colour, c in zip(T["tone"], class_counts(g)):
            share = c / len(g)
            if share:
                ax.bar(i, share, bottom=bottom, width=0.78, color=colour, edgecolor=T["bg"], linewidth=1)
            bottom += share
        ax.text(i, 1.02, str(len(g)), ha="center", va="bottom", fontsize=8.5, color=T["muted"])
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    grid_y(ax)
    week_ticks(ax)
    events(ax, week_x, base=1.08)
    title(ax, "Share of Nvidia/Jensen headlines by ethics tone, per week (count above bar)", 66)
    legend(ax, CLASS_NAMES, T["tone"])
    finish(fig, path)


def daily_chart(rows, path):
    start = date(2026, 10, 26)
    days = [start + timedelta(days=i) for i in range(17)]
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    top = 0
    for i, d in enumerate(days):
        bottom = 0
        for colour, c in zip(T["tone"], class_counts([r for r in rows if r["date"] == d])):
            if c:
                ax.bar(i, c, bottom=bottom, width=0.74, color=colour, edgecolor=T["bg"], linewidth=1)
            bottom += c
        top = max(top, bottom)
    ax.set_ylim(0, top * 1.12)
    grid_y(ax)
    ax.set_xticks(range(0, 17, 2), [days[i].strftime("%-d %b") for i in range(0, 17, 2)])
    ax.set_xlim(-0.7, 16.7)
    events(ax, lambda d: (d - start).days)
    ax.set_ylabel("Headlines per day")
    title(ax, "The 17 days around the election", 60)
    legend(ax, CLASS_NAMES, T["tone"])
    finish(fig, path)


def outlet_chart(summary, path):
    outlets = [o for o in OUTLETS if o in summary["by_outlet"]][::-1]
    fig, ax = plt.subplots(figsize=(11, 3.6), dpi=160)
    before_c, after_c = T["tone"][2], T["tone"][0]
    for i, o in enumerate(outlets):
        b, a = summary["by_outlet"][o]["before_2026-10-29"], summary["by_outlet"][o]["from_2026-11-03"]
        bs, as_ = b["ethics_negative_share"], a["ethics_negative_share"]
        ax.plot([bs, as_], [i, i], color=T["grid"], lw=3, zorder=1, solid_capstyle="round")
        ax.scatter(bs, i, s=90, color=before_c, zorder=2, edgecolor=T["bg"], linewidth=2)
        ax.scatter(as_, i, s=90, color=after_c, zorder=2, edgecolor=T["bg"], linewidth=2)
        ax.annotate(f"{bs:.0%}  (n={b['n']})", (bs, i), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=9, color=T["muted"])
        ax.annotate(f"{as_:.0%}  (n={a['n']})", (as_, i), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=9, color=T["ink"])
    ax.set_yticks(range(len(outlets)), outlets)
    ax.set_ylim(-0.6, len(outlets) - 0.3)
    ax.set_xlim(-0.05, 1.08)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.xaxis.grid(True, color=T["grid"], lw=0.8)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=T["ink"])
    title(ax, "Ethics-negative share of headlines: before 29 Oct (grey) vs from 3 Nov (red)", 12)
    finish(fig, path)


def volume_chart(rows, path):
    """Headlines per week, stacked by outlet."""
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    top = 0
    for i, w in enumerate(weeks()):
        bottom = 0
        for o in OUTLETS:
            c = sum(1 for r in rows if r["outlet"] == o and in_week(r, w))
            if c:
                ax.bar(i, c, bottom=bottom, width=0.78, color=T["outlet"][o], edgecolor=T["bg"], linewidth=1)
            bottom += c
        top = max(top, bottom)
        if bottom:
            ax.text(i, bottom + 1, str(bottom), ha="center", va="bottom", fontsize=8.5, color=T["muted"], zorder=5,
                    bbox={"boxstyle": "square,pad=0.15", "facecolor": T["bg"], "edgecolor": "none"})
    ax.set_ylim(0, top * 1.12)
    grid_y(ax)
    week_ticks(ax)
    events(ax, week_x)
    ax.set_ylabel("Headlines per week")
    title(ax, "How many Nvidia/Jensen headlines each outlet ran, per week", 60)
    totals = {o: sum(r["outlet"] == o for r in rows) for o in OUTLETS}
    legend(ax, [f"{o} ({totals[o]})" for o in OUTLETS], [T["outlet"][o] for o in OUTLETS], ncol=3)
    finish(fig, path)


def outlet_tone_chart(rows, path):
    """Mean median-score per outlet per month, with headline counts."""
    months = [(2026, m) for m in range(5, 12)]
    labels = [date(y, m, 1).strftime("%b") for y, m in months]
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    ax.axhline(0, color=T["grid"], lw=1.2, zorder=1)
    for k, o in enumerate(OUTLETS):
        xs, ys, ns, idx = [], [], [], []
        for i, (y, m) in enumerate(months):
            g = [r for r in rows if r["outlet"] == o and r["date"].year == y and r["date"].month == m]
            if g:
                xs.append(i + (k - 1) * 0.06)
                ys.append(sum(r["median_score"] for r in g) / len(g))
                ns.append(len(g))
                idx.append(i)
        for j in range(len(xs) - 1):
            gap = idx[j + 1] - idx[j] > 1  # a month with no headlines: dashed, thinner
            ax.plot(xs[j:j + 2], ys[j:j + 2], color=T["outlet"][o], lw=1.2 if gap else 2,
                    ls=(0, (3, 3)) if gap else "-", alpha=0.7 if gap else 1, zorder=2)
        ax.scatter(xs, ys, s=[max(30, min(160, 12 * n)) for n in ns], color=T["outlet"][o],
                   edgecolor=T["bg"], linewidth=2, zorder=3)
        ax.annotate(f"{o}  {ys[-1]:+.2f}", (xs[-1], ys[-1]), xytext=(10, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=T["ink"])
    ax.set_xticks(range(len(months)), labels)
    ax.set_xlim(-0.4, len(months) - 0.1 + 0.9)
    ax.set_ylim(-2.1, 0.5)
    ax.set_yticks([-2, -1.5, -1, -0.5, 0, 0.5], ["−2", "−1.5", "−1", "−0.5", "0", "+0.5"])
    grid_y(ax)
    ax.set_ylabel("Mean ethics score (−2 to +2)")
    ax.annotate("Dot size shows how many headlines that month. Dashed: a month with no headlines from that outlet.",
                (0, 0.42), fontsize=9, color=T["muted"], va="top")
    title(ax, "Average ethics tone by outlet, per month (Nov = 1–11 Nov)", 12)
    finish(fig, path)


def rater_chart(rows, summary, path):
    """Score distribution for each rater, side by side."""
    scores = [-2, -1, 0, 1, 2]
    raters = [("Rater A", "rater_a"), ("Rater B", "rater_b"), ("Rater C", "rater_c")]
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=160)
    w = 0.26
    top = 0
    for k, (name, key) in enumerate(raters):
        counts = [sum(r[key] == s for r in rows) for s in scores]
        top = max(top, max(counts))
        xs = [i + (k - 1) * w for i in range(len(scores))]
        ax.bar(xs, counts, width=w - 0.03, color=T["rater"][k], edgecolor=T["bg"], linewidth=1, label=name)
        for x, c in zip(xs, counts):
            ax.text(x, c + 2, str(c), ha="center", va="bottom", fontsize=8.5, color=T["muted"])
    ax.set_xticks(range(len(scores)), ["−2 strongly\nnegative", "−1 mildly\nnegative", "0 no ethics\ncontent",
                                        "+1 defends", "+2 praises"])
    ax.set_ylim(0, top * 1.15)
    grid_y(ax)
    ax.set_ylabel("Headlines")
    ag = summary["agreement"]
    title(ax, f"Three raters, scored separately: identical on {ag['all_three_identical']} of {len(rows)} "
              f"headlines, never more than {ag['max_spread']} point apart", 12)
    ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    finish(fig, path)


def og_image(rows, summary, path):
    """1280x640 social preview: title, the headline numbers and a weekly sparkline of negative share."""
    use_theme("dark")
    bg = "#14161a"
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100)
    fig.patch.set_facecolor(bg)
    before = summary["periods"]["before_story_2026-05-11_to_10-28"]["ethics_negative_share"]
    after = summary["periods"]["election_and_after_2026-11-03_to_11-11"]["ethics_negative_share"]
    fig.text(0.06, 0.86, "NVIDIA HEADLINES · WSJ · NYT · THE ECONOMIST · MAY–NOV 2026",
             color="#9a9fa6", fontsize=15, fontweight="bold")
    fig.text(0.06, 0.70, "How ethics coverage of Jensen Huang turned", color="#e8e9ea",
             fontsize=36, fontweight="bold")
    fig.text(0.06, 0.53, f"{before:.0%}", color="#9a9fa6", fontsize=64, fontweight="bold")
    fig.text(0.215, 0.555, "ethics-negative\nbefore 29 Oct", color="#9a9fa6", fontsize=15)
    fig.text(0.47, 0.53, f"{after:.0%}", color="#e0594f", fontsize=64, fontweight="bold")
    fig.text(0.625, 0.555, "from the 3 Nov\nmidterms onward", color="#e8e9ea", fontsize=15)
    ax = fig.add_axes([0.06, 0.12, 0.88, 0.30])
    ax.set_facecolor(bg)
    for i, w in enumerate(weeks()):
        g = [r for r in rows if in_week(r, w)]
        if g:
            share = sum(r["median_score"] < 0 for r in g) / len(g)
            ax.bar(i, max(share, 0.015), width=0.72,
                   color="#e0594f" if w >= STORY_BREAK - timedelta(days=3) else "#5b5f66")
    xe = week_x(MIDTERMS)
    ax.axvline(xe, color="#e8e9ea", lw=1.5, ls=(0, (4, 3)))
    ax.text(xe - 0.3, 0.98, "midterms", color="#e8e9ea", fontsize=13, ha="right", va="top")
    ax.set_ylim(0, 1)
    ax.set_xlim(-0.7, 26.7)
    ax.axis("off")
    scanned = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))["headlines_listed_total"]
    fig.text(0.06, 0.05, f"{scanned:,} headlines scanned · {summary['headlines']} mention Nvidia or Jensen · "
             f"three independent raters · bars: weekly share ethics-negative", color="#9a9fa6", fontsize=13)
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


# ---------- one-image summary (portrait, phone-friendly) ----------

def content_kind(url):
    import re
    if "/livecoverage/" in url:
        return "Live-blog cards"
    if re.search(r"/podcasts?/|/video/|/audio/", url):
        return "Podcasts & video"
    if re.search(r"/newsletters?/|/the-morning|/briefing|/the-evening", url):
        return "Newsletters"
    return "Articles"


def poster(rows, summary, path):
    import matplotlib.gridspec as gridspec
    corpus = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(9, 15.5), dpi=150)
    gs = gridspec.GridSpec(5, 1, figure=fig, height_ratios=[1.45, 1.15, 1.25, 1.3, 1.15],
                           hspace=0.62, left=0.1, right=0.9, top=0.975, bottom=0.065)

    # 1. header
    ax = fig.add_subplot(gs[0]); ax.axis("off")
    before = summary["periods"]["before_story_2026-05-11_to_10-28"]["ethics_negative_share"]
    after = summary["periods"]["election_and_after_2026-11-03_to_11-11"]["ethics_negative_share"]
    ax.text(0, 1.0, "NVIDIA HEADLINES · WSJ · NYT · THE ECONOMIST · MAY–NOV 2026", transform=ax.transAxes,
            fontsize=10.5, fontweight="bold", color=T["muted"], va="top")
    ax.text(0, 0.87, "How ethics coverage of\nJensen Huang turned", transform=ax.transAxes,
            fontsize=24, fontweight="bold", color=T["ink"], va="top", linespacing=1.05)
    ax.text(0, 0.17, f"{before:.0%}", transform=ax.transAxes, fontsize=44, fontweight="bold", color=T["muted"], va="bottom")
    ax.text(0.2, 0.21, "ethics-negative\nbefore 29 Oct", transform=ax.transAxes, fontsize=11, color=T["muted"], va="bottom")
    ax.text(0.47, 0.17, f"{after:.0%}", transform=ax.transAxes, fontsize=44, fontweight="bold", color=T["tone"][0], va="bottom")
    ax.text(0.71, 0.21, "from the 3 Nov\nmidterms onward", transform=ax.transAxes, fontsize=11, color=T["ink"], va="bottom")
    ax.text(0, 0.06, "The turn began 29 Oct, five days before the vote, when the spy-plot story broke.\n"
            "The surge came 8–9 Nov, after Huang admitted an affair and the board opened a probe.",
            transform=ax.transAxes, fontsize=10, color=T["muted"], va="top", linespacing=1.4)

    def panel_title(ax, text):
        ax.set_title(text, loc="left", fontsize=12.5, fontweight="bold", color=T["ink"], pad=26)

    # 2. weekly ethics-negative share
    ax = fig.add_subplot(gs[1])
    for i, w in enumerate(weeks()):
        g = [r for r in rows if in_week(r, w)]
        if g:
            share = sum(r["median_score"] < 0 for r in g) / len(g)
            ax.bar(i, max(share, 0.012), width=0.74,
                   color=T["tone"][0] if w + timedelta(days=6) >= STORY_BREAK else T["tone"][2])
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.5, 1], ["0%", "50%", "100%"])
    grid_y(ax); week_ticks(ax)
    events(ax, week_x, base=1.03, step=0.11, fontsize=9)
    panel_title(ax, "1  Share of headlines that are ethics-negative, per week")
    ax.title.set_position((0, 1.30))

    # 3. volume by outlet
    ax = fig.add_subplot(gs[2])
    top = 0
    for i, w in enumerate(weeks()):
        bottom = 0
        for o in OUTLETS:
            c = sum(1 for r in rows if r["outlet"] == o and in_week(r, w))
            if c:
                ax.bar(i, c, bottom=bottom, width=0.74, color=T["outlet"][o], edgecolor=T["bg"], linewidth=0.8)
            bottom += c
        top = max(top, bottom)
    ax.set_ylim(0, top * 1.1)
    grid_y(ax); week_ticks(ax)
    events(ax, week_x, base=1.03, step=0.10, fontsize=9)
    ax.annotate("110 headlines in the week of 9 Nov.\nBusiest earlier week: 31 (earnings).", (19.2, top * 0.72),
                fontsize=9.5, color=T["muted"], ha="right", va="center")
    totals = {o: sum(r["outlet"] == o for r in rows) for o in OUTLETS}
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=T["outlet"][o]) for o in OUTLETS],
              [f"{o} ({totals[o]})" for o in OUTLETS], ncol=3, frameon=False, loc="upper left",
              bbox_to_anchor=(0, 0.98), fontsize=9.5, handlelength=1, handleheight=1)
    panel_title(ax, "2  Headlines per week, by outlet")
    ax.title.set_position((0, 1.30))

    # 4. monthly tone by outlet
    ax = fig.add_subplot(gs[3])
    months = [(2026, m) for m in range(5, 12)]
    ax.axhline(0, color=T["grid"], lw=1.2)
    for k, o in enumerate(OUTLETS):
        xs, ys, ns, idx = [], [], [], []
        for i, (y, m) in enumerate(months):
            g = [r for r in rows if r["outlet"] == o and r["date"].month == m]
            if g:
                xs.append(i + (k - 1) * 0.06); ys.append(sum(r["median_score"] for r in g) / len(g))
                ns.append(len(g)); idx.append(i)
        for j in range(len(xs) - 1):
            gap = idx[j + 1] - idx[j] > 1
            ax.plot(xs[j:j + 2], ys[j:j + 2], color=T["outlet"][o], lw=1.2 if gap else 2,
                    ls=(0, (3, 3)) if gap else "-", alpha=0.7 if gap else 1)
        ax.scatter(xs, ys, s=[max(24, min(130, 10 * n)) for n in ns], color=T["outlet"][o],
                   edgecolor=T["bg"], linewidth=1.5, zorder=3)
        ax.annotate(f"{o}  {ys[-1]:+.2f}".replace("-", "−"), (xs[-1], ys[-1]), xytext=(9, 0),
                    textcoords="offset points", va="center", fontsize=9.5, color=T["ink"])
    ax.set_xticks(range(7), [date(2026, m, 1).strftime("%b") for _, m in months])
    ax.set_xlim(-0.3, 8.2)
    ax.set_ylim(-2.15, 0.35)
    ax.set_yticks([-2, -1, 0], ["−2", "−1", "0"])
    grid_y(ax)
    ax.set_ylabel("Mean score (−2 to +2)")
    ax.text(0, 1.0, "Dot size = headlines that month · dashed = a month with none", transform=ax.transAxes,
            fontsize=9, color=T["muted"], va="bottom")
    panel_title(ax, "3  Average ethics tone by outlet, per month (Nov = 1–11 Nov)")

    # 5. normal week vs 9–11 Nov, by format
    ax = fig.add_subplot(gs[4])
    kinds = ["Articles", "Live-blog cards", "Podcasts & video", "Newsletters"]
    kind_col = [T["ink"], T["muted"], T["tone"][2], T["grid"]]
    pre_weeks = 24
    labels, ypos = [], []
    y = 0
    for o in ["NYT", "WSJ"]:
        pre = [r for r in rows if r["outlet"] == o and r["date"] < date(2026, 10, 26)]
        surge = [r for r in rows if r["outlet"] == o and date(2026, 11, 9) <= r["date"] <= date(2026, 11, 11)]
        for label, g, scale in ((f"{o}: a normal week, May–Oct", pre, pre_weeks), (f"{o}: 9–11 Nov (3 days)", surge, 1)):
            left = 0.0
            for kname, kc in zip(kinds, kind_col):
                v = sum(content_kind(r["url"]) == kname for r in g) / scale
                if v:
                    ax.barh(y, v, left=left, height=0.62, color=kc, edgecolor=T["bg"], linewidth=0.8)
                left += v
            ax.text(left + 0.8, y, f"{left:.1f}" if scale > 1 else f"{int(left)}", va="center",
                    fontsize=10, color=T["ink"], fontweight="bold")
            ax.text(0, y + 0.42, label, fontsize=9.5, color=T["ink"], va="bottom")
            y -= 1.25
        y -= 0.35
    ax.set_yticks([])
    ax.set_ylim(y + 0.75, 0.95)
    ax.spines["left"].set_visible(False)
    ax.xaxis.grid(True, color=T["grid"], lw=0.8); ax.set_axisbelow(True)
    ax.set_xlim(0, 72)
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in kind_col], kinds, ncol=4, frameon=False,
              loc="upper left", bbox_to_anchor=(-0.02, 1.16), fontsize=9, handlelength=1, handleheight=1)
    panel_title(ax, "4  A normal week vs three days: NYT ran more articles on 9–11 Nov (30)\n    than in the previous 5½ months (25)")
    ax.title.set_position((0, 1.12))

    fig.text(0.1, 0.012,
             f"Source: {corpus['headlines_listed_total']:,} WSJ, NYT and Economist headlines scanned, 11 May–11 Nov 2026; "
             f"{len(rows)} mention Nvidia or Jensen,\neach scored by three independent raters. "
             "github.com/twobitapps/nvidia-headlines-ethics-2026",
             fontsize=8.5, color=T["muted"], va="bottom", linespacing=1.4)
    fig.savefig(path)
    plt.close(fig)


# ---------- README headline list ----------

TONE_MARK = {-2: "🟥", -1: "🟧", 0: "⬜", 1: "🟩", 2: "🟩"}
START, END = "<!-- HEADLINES:START -->", "<!-- HEADLINES:END -->"


def readme_table(rows):
    """Rewrite the headline list in README.md between the HEADLINES markers, newest first."""
    sign = lambda s: f"+{s}" if s > 0 else str(s)
    cell = lambda t: t.replace("|", "\\|").replace("\n", " ").strip()
    lines = [
        START,
        f"<details open>\n<summary><b>All {len(rows)} scored headlines</b> (newest first)</summary>\n",
        "🟥 strongly negative · 🟧 mildly negative · ⬜ no ethics content · 🟩 defends or praises\n",
        "| Date | Outlet | Median | Raters A / B / C | Headline |",
        "|---|---|:-:|:-:|---|",
    ]
    for r in sorted(rows, key=lambda r: (r["date"], r["id"]), reverse=True):
        s = r["median_score"]
        raters = " / ".join(sign(r[k]) for k in ("rater_a", "rater_b", "rater_c"))
        lines.append(f"| {r['date'].isoformat()} | {r['outlet']} | {TONE_MARK[s]} {sign(s)} | {raters} | "
                     f"[{cell(r['headline'])}]({r['url']}) |")
    lines += ["", "</details>", END]
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = "\n".join(lines)
    if START in text and END in text:
        text = text[: text.index(START)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    readme.write_text(text, encoding="utf-8")


CHART_SET = {
    "weekly-share": lambda rows, s, p: weekly_chart(rows, p),
    "daily-around-election": lambda rows, s, p: daily_chart(rows, p),
    "by-outlet": lambda rows, s, p: outlet_chart(s, p),
    "volume-by-outlet": lambda rows, s, p: volume_chart(rows, p),
    "tone-by-outlet-monthly": lambda rows, s, p: outlet_tone_chart(rows, p),
    "rater-distributions": lambda rows, s, p: rater_chart(rows, s, p),
}


def main():
    rows = load()
    assert all(WINDOW_START <= r["date"] <= WINDOW_END for r in rows)
    summary = summarise(rows)
    (ROOT / "data" / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    CHARTS.mkdir(exist_ok=True)
    global SOURCE
    SOURCE = source_line(rows)
    use_theme(CHART_THEME)
    for name, draw in CHART_SET.items():
        draw(rows, summary, CHARTS / f"{name}.png")
    use_theme(CHART_THEME)
    poster(rows, summary, CHARTS / "summary.png")
    og_image(rows, summary, ROOT / "og-image.png")
    readme_table(rows)
    p = summary["periods"]
    print(json.dumps({k: (v["n"], v["ethics_negative_share"], v["mean_score"]) for k, v in p.items()}, indent=1))


if __name__ == "__main__":
    main()
