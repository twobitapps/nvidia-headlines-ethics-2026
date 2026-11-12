"""Recompute every figure and chart in this repo from data/headlines.csv.

Usage (from the repo root):
    pip install matplotlib==3.9.2 pillow==10.4.0
    python scripts/analyze.py

Writes data/summary.json, charts/*.png and og-image.png.
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
ADMISSION = date(2026, 11, 8)

# Ethics tone classes, most negative first. Colours: two warm steps for negative,
# a neutral grey for "no ethics content", one cool hue for positive.
CLASSES = [
    ("Strongly negative", "#b3261e", lambda s: s <= -2),
    ("Mildly negative", "#e9965a", lambda s: s == -1),
    ("No ethics content", "#c4c6c9", lambda s: s == 0),
    ("Defends or praises", "#2b7a78", lambda s: s >= 1),
]
INK, MUTED, GRID, BG = "#1d1f22", "#62666c", "#e8e8e4", "#ffffff"


def pick_font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"):
        if name in names:
            return name
    return "DejaVu Sans"


plt.rcParams.update({
    "font.family": pick_font(), "font.size": 10.5, "text.color": INK,
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
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


def class_counts(rows):
    return [sum(test(r["median_score"]) for r in rows) for _, _, test in CLASSES]


def marker(ax, x, label, y, ha):
    ax.axvline(x, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=3)
    ax.annotate(label, (x, y), xycoords=("data", "axes fraction"), ha=ha, va="bottom",
                fontsize=9.5, fontweight="semibold", color=INK,
                xytext=(4 if ha == "left" else -4, 0), textcoords="offset points")


def legend(ax, ncol=4):
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c, _ in CLASSES]
    ax.legend(handles, [n for n, _, _ in CLASSES], ncol=ncol, frameon=False,
              loc="upper left", bbox_to_anchor=(0, -0.13), fontsize=9.5, handlelength=1, handleheight=1)


def weekly_chart(rows, path):
    weeks = [WINDOW_START + timedelta(days=7 * i) for i in range(27)]
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    for i, w in enumerate(weeks):
        g = [r for r in rows if w <= r["date"] < w + timedelta(days=7)]
        if not g:
            continue
        bottom = 0.0
        for (name, colour, _), c in zip(CLASSES, class_counts(g)):
            share = c / len(g)
            if share:
                ax.bar(i, share, bottom=bottom, width=0.78, color=colour, edgecolor=BG, linewidth=1)
            bottom += share
        ax.text(i, 1.02, str(len(g)), ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(range(0, 27, 3), [weeks[i].strftime("%-d %b") for i in range(0, 27, 3)])
    ax.set_xlim(-0.7, 26.7)
    to_x = lambda d: (d - WINDOW_START).days / 7 - 0.5
    marker(ax, to_x(STORY_BREAK), "29 Oct: spy-plot story breaks", 1.09, "right")
    marker(ax, to_x(MIDTERMS), "3 Nov: midterms", 1.09, "left")
    ax.set_title("Share of Nvidia/Jensen headlines by ethics tone, per week (count above bar)",
                 loc="left", fontsize=12.5, fontweight="semibold", pad=40)
    legend(ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def daily_chart(rows, path):
    start = date(2026, 10, 26)
    days = [start + timedelta(days=i) for i in range(17)]
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
    top = 0
    for i, d in enumerate(days):
        bottom = 0
        for (name, colour, _), c in zip(CLASSES, class_counts([r for r in rows if r["date"] == d])):
            if c:
                ax.bar(i, c, bottom=bottom, width=0.74, color=colour, edgecolor=BG, linewidth=1)
            bottom += c
        top = max(top, bottom)
    ax.set_ylim(0, top * 1.12)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(range(0, 17, 2), [days[i].strftime("%-d %b") for i in range(0, 17, 2)])
    ax.set_xlim(-0.7, 16.7)
    marker(ax, (STORY_BREAK - start).days, "29 Oct: spy-plot story breaks", 1.02, "left")
    marker(ax, (MIDTERMS - start).days, "3 Nov: midterms", 1.10, "left")
    ax.annotate("Huang admits affair,\nboard opens probe (8–9 Nov)", ((ADMISSION - start).days + 0.45, top * 0.92),
                ha="right", va="top", fontsize=9.5, color=MUTED)
    ax.set_ylabel("Headlines per day")
    ax.set_title("The 17 days around the election", loc="left", fontsize=12.5,
                 fontweight="semibold", pad=34)
    legend(ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def outlet_chart(summary, path):
    outlets = list(summary["by_outlet"])
    fig, ax = plt.subplots(figsize=(11, 3.6), dpi=160)
    y = range(len(outlets))
    before = [summary["by_outlet"][o]["before_2026-10-29"]["ethics_negative_share"] for o in outlets]
    after = [summary["by_outlet"][o]["from_2026-11-03"]["ethics_negative_share"] for o in outlets]
    nb = [summary["by_outlet"][o]["before_2026-10-29"]["n"] for o in outlets]
    na = [summary["by_outlet"][o]["from_2026-11-03"]["n"] for o in outlets]
    for i in y:
        ax.plot([before[i], after[i]], [i, i], color=GRID, lw=3, zorder=1, solid_capstyle="round")
        ax.scatter(before[i], i, s=90, color="#c4c6c9", zorder=2, edgecolor=BG, linewidth=2)
        ax.scatter(after[i], i, s=90, color="#b3261e", zorder=2, edgecolor=BG, linewidth=2)
        ax.annotate(f"{before[i]:.0%}  (n={nb[i]})", (before[i], i), xytext=(0, 10),
                    textcoords="offset points", ha="center", fontsize=9, color=MUTED)
        ax.annotate(f"{after[i]:.0%}  (n={na[i]})", (after[i], i), xytext=(0, 10),
                    textcoords="offset points", ha="center", fontsize=9, color=INK)
    ax.set_yticks(list(y), outlets)
    ax.set_ylim(-0.6, len(outlets) - 0.3)
    ax.set_xlim(-0.05, 1.08)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=INK)
    ax.set_title("Ethics-negative share of headlines: before 29 Oct (grey) vs from 3 Nov (red)",
                 loc="left", fontsize=12.5, fontweight="semibold", pad=12)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def og_image(rows, summary, path):
    """1280x640 social preview: title, the headline numbers and a weekly sparkline of negative share."""
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100)
    fig.patch.set_facecolor("#14161a")
    before = summary["periods"]["before_story_2026-05-11_to_10-28"]["ethics_negative_share"]
    after = summary["periods"]["election_and_after_2026-11-03_to_11-11"]["ethics_negative_share"]
    fig.text(0.06, 0.86, "NVIDIA HEADLINES · WSJ · NYT · THE ECONOMIST · MAY–NOV 2026",
             color="#9a9fa6", fontsize=15, fontweight="semibold")
    fig.text(0.06, 0.70, "How ethics coverage of Jensen Huang turned", color="#e8e9ea",
             fontsize=36, fontweight="bold")
    fig.text(0.06, 0.53, f"{before:.0%}", color="#9a9fa6", fontsize=64, fontweight="bold")
    fig.text(0.215, 0.555, "ethics-negative\nbefore 29 Oct", color="#9a9fa6", fontsize=15)
    fig.text(0.47, 0.53, f"{after:.0%}", color="#e0594f", fontsize=64, fontweight="bold")
    fig.text(0.625, 0.555, "from the 3 Nov\nmidterms onward", color="#e8e9ea", fontsize=15)
    ax = fig.add_axes([0.06, 0.12, 0.88, 0.30])
    ax.set_facecolor("#14161a")
    weeks = [WINDOW_START + timedelta(days=7 * i) for i in range(27)]
    for i, w in enumerate(weeks):
        g = [r for r in rows if w <= r["date"] < w + timedelta(days=7)]
        if g:
            share = sum(r["median_score"] < 0 for r in g) / len(g)
            ax.bar(i, max(share, 0.015), width=0.72, color="#e0594f" if w >= STORY_BREAK - timedelta(days=3) else "#5b5f66")
    xe = (MIDTERMS - WINDOW_START).days / 7 - 0.5
    ax.axvline(xe, color="#e8e9ea", lw=1.5, ls=(0, (4, 3)))
    ax.text(xe - 0.3, 0.98, "midterms", color="#e8e9ea", fontsize=13, ha="right", va="top")
    ax.set_ylim(0, 1)
    ax.set_xlim(-0.7, 26.7)
    ax.axis("off")
    fig.text(0.06, 0.05, f"{summary['headlines']} headlines · three independent raters · weekly share of ethics-negative headlines",
             color="#9a9fa6", fontsize=13)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


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


def main():
    rows = load()
    assert all(WINDOW_START <= r["date"] <= WINDOW_END for r in rows)
    summary = summarise(rows)
    (ROOT / "data" / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    CHARTS.mkdir(exist_ok=True)
    weekly_chart(rows, CHARTS / "weekly-share.png")
    daily_chart(rows, CHARTS / "daily-around-election.png")
    outlet_chart(summary, CHARTS / "by-outlet.png")
    og_image(rows, summary, ROOT / "og-image.png")
    readme_table(rows)
    p = summary["periods"]
    print(json.dumps({k: (v["n"], v["ethics_negative_share"], v["mean_score"]) for k, v in p.items()}, indent=1))
    print(json.dumps(summary["agreement"], indent=1))


if __name__ == "__main__":
    main()
