# Nvidia headlines and ethics sentiment, May–Nov 2026

![How ethics coverage of Jensen Huang turned](og-image.png)

Every headline containing "Nvidia" or "Jensen" published by **The Wall Street Journal**, **The New York Times** and **The Economist** between 11 May and 11 Nov 2026, scored for ethics sentiment. The question was whether coverage of Jensen Huang turned negative after the US midterm elections on 3 Nov 2026.

## Finding

| Period | Headlines | Ethics-negative | Mean score (−2 to +2) |
|---|---:|---:|---:|
| 11 May – 28 Oct | 144 | 6% | −0.05 |
| 29 Oct – 2 Nov (spy-plot story breaks) | 4 | 100% | −1.75 |
| **3 – 11 Nov (election and after)** | **120** | **82%** | **−1.12** |
| of which 3 – 7 Nov | 5 | 60% | −0.80 |
| of which 8 – 11 Nov | 115 | 83% | −1.14 |

Sentiment did turn after the election, but the election is not what turned it.

- The break came on **29 Oct**, five days before the vote, when the NYT reported that Huang was seen as the target of a Chinese spy plot.
- The surge came on **8–9 Nov**, when Huang acknowledged an affair and Nvidia's board opened a probe. 115 of the 120 post-election headlines are from 8–11 Nov.
- The data cannot separate an election effect from the scandal, because the post-election period is almost entirely one news cycle about one story.

Headlines about Huang himself went from a mean of −0.06 before 29 Oct (17 headlines) to −1.18 from 3 Nov (79 headlines).

![Weekly share by ethics tone](charts/weekly-share.png)

![Daily headlines around the election](charts/daily-around-election.png)

![Before and after by outlet](charts/by-outlet.png)

An interactive version, with every headline and its scores, is in [`site/index.html`](site/index.html).

## Was the negativity written in?

A separate audit of how the headlines are worded is in [`analysis/framing-audit.md`](analysis/framing-audit.md). It ran on the first 168 headlines. In short:

- **Verdict:** no evidence of deliberate negative framing, at about 75% confidence. Headlines cannot show intent. The tone is mostly carried by the facts reported.
- **Lapses:** there are specific, checkable lapses that all point against Huang.
  - Spy claims are stated more firmly than the outlets' own summaries support.
  - NYT's "Halted" describes an inquiry that was moved.
  - WSJ's "Downfall" ran on a day its other headlines said "possible exit".
  - "Plunge" describes a 4.3% fall.
  - Alice Huang is mostly called "woman", or a sexualised term, rather than an executive.
- **Counter-framing:** sympathetic headlines appear throughout, and WSJ repeated good news (the Hugging Face deal) just as heavily.

## Method

**Collection.** Headlines were read on 11–12 Nov 2026 from each outlet's public listing pages in a desktop browser:
- **WSJ:** the daily news archive for all 185 days, plus site search.
- **NYT:** the daily sitemaps for all 185 days, plus site search for "Nvidia" and "Jensen".
- **The Economist:** the 26 weekly editions and site search.

A headline was kept if it contains "Nvidia" or "Jensen" (case-insensitive) and is dated in the window. Exact duplicates within an outlet were removed, leaving 268: WSJ 177, NYT 80, The Economist 11. No article text was collected or stored.

**Scoring.** Three Claude Opus 5.5 instances scored every headline independently. Each saw only the headline and the outlet's one-line summary, not the other raters' scores. The rubric:

| Score | Meaning |
|---:|---|
| −2 | Strongly negative on ethics or integrity: misconduct, spying, deception, cover-up, infidelity scandal, improper influence, calls for resignation |
| −1 | Mildly negative: scrutiny, an investigation of a deal, governance or conflict-of-interest concerns, safety or ethics debate, risk of misuse, accounting doubts, a scandal's market consequences |
| 0 | No ethics content: ordinary business, products, earnings, stock moves unrelated to a scandal |
| +1 | Mildly positive: defends or sympathises with Huang or Nvidia on integrity, reports a denial |
| +2 | Strongly positive: clear praise of ethical conduct, exoneration |

The charts use the median of the three scores. "Ethics-negative" means a median of −1 or −2.

**Agreement.**

| Raters | Same score | Quadratic weighted kappa |
|---|---:|---:|
| A and B | 92.9% | 0.95 |
| A and C | 94.4% | 0.96 |
| B and C | 94.0% | 0.95 |

All three gave the same score on 243 of 268 headlines and never differed by more than one point. The before-and-after gap holds for each rater alone: 5–7% ethics-negative before 29 Oct, 79–82% from 3 Nov.

## Limitations

- **Shared blind spots:** the three raters are the same model using one rubric, so they share any blind spot in it. High agreement shows consistency, not correctness. Human raters would be a stronger check.
- **Scores track volume:** most headlines are plain business news and score 0, so the means largely track how many scandal headlines there are.
- **WSJ:** the WSJ daily archive leaves out live-coverage posts, videos and podcasts. Those are included only where site search found them, so they are undercounted before November. WSJ also re-headlines one event many times a day across live blogs, newsletters and podcasts, which inflates November counts.
- **The Economist:** coverage is incomplete. Access was interrupted partway through, and some candidate articles were not checked, so its 11 headlines are a floor. Pieces whose headline does not contain "Nvidia" or "Jensen" are excluded by design, even when they are about the affair.
- **Dates:** WSJ dates are US Eastern. Some dates are a day off from the publication time because of time-zone or update-time effects.
- **Claims:** the spy and affair claims are as reported by these outlets and were not independently verified.

## Files

| Path | What it is |
|---|---|
| `data/headlines.csv`, `data/headlines.json` | One row per headline: `id`, `outlet`, `date`, `headline`, `print_headline` (Economist print title where it differs), `url`, `rater_a`, `rater_b`, `rater_c`, `median_score`, `about_huang` (1 if the headline names Huang or the CEO) |
| `data/summary.json` | Every figure above, computed from the CSV |
| `scripts/analyze.py` | Recomputes `summary.json`, the charts and the preview image from the CSV |
| `charts/` | The three charts above |
| `site/index.html` | Interactive chart and full headline list |
| `analysis/framing-audit.md` | Headline wording audit |

To reproduce:

```
pip install matplotlib pillow
python scripts/analyze.py
```

## Rights

Headlines remain the property of their publishers and are reproduced here, with links to the originals, only as the subject of this analysis. The repo contains no article text. The scores, summary figures, charts and written analysis are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code is under the MIT License (see `LICENSE`).
