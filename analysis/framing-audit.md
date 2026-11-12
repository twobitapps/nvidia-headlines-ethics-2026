# Headline framing audit

How the headlines about Nvidia and Jensen Huang were written in the WSJ, the NYT and The Economist, 11 May to 11 Nov 2026, and whether the wording shows signs of deliberate negative framing.

This audit was run by a separate Claude Opus 5.5 instance on the first collection pass (168 headlines: WSJ 104, NYT 55, Economist 9), before the full archive crawl brought the set to 268. It saw headlines and the short summary line each outlet shows under them in its listings. It did not see article text. Headlines are quoted exactly. Summary lines are paraphrased here, because this repo publishes headlines only.

## 0. What this data can and cannot support

- **Sampling was uneven in the first pass.** WSJ search returned at most 30 results per query, so May to October WSJ was undercounted and November WSJ well covered. Any WSJ before-and-after volume comparison overstates the jump. NYT was the only outlet whose volume compared fairly across periods. The later archive crawl (see the README) closed most of the WSJ gap.
- **Headlines only.** The audit can judge how a headline is written, not whether the article is fair.
- **Dates are day-level.** There are no times of day, so a late-evening US story that carries the next day's date cannot be confirmed or ruled out.
- **Each headline is a snapshot.** Several WSJ URL slugs show an earlier headline that was later rewritten (section 7).

## 1. Opinion and analysis versus straight news

The 94 scandal-period items (29 Oct to 11 Nov, unrelated market items removed) were coded by format using the URL section and listing cues. "Loaded" means the headline contains an evaluative or emotive word that the reported fact does not require. "Pro/defensive" means the headline carries a view favourable to Huang or skeptical of the case against him.

| Format | n | Loaded | Pro/defensive |
|---|---|---|---|
| Opinion / signed column | 7 | 6 (86%) | 2 |
| Analysis (Heard on the Street-type, DealBook, Economist business) | 10 | 4 (40%) | 2 |
| Podcast / video / briefing | 16 | 6 (38%) | 0 |
| Straight news / explainer | 36 | 10 (28%) | 1 |
| Newsletter roundups | 8 | 2 (25%) | 1 |
| WSJ live-blog cards | 17 | 1 (6%) | 2 |

**Opinion and columns:** "Nvidia Gets a Chinese Honeypot Lesson" (WSJ, 11-09); "The Temptation of Jensen Huang" (WSJ, 11-10); "China's Jensen Huang Caper" (WSJ, 11-10); "Jensen Huang Is Only Human" (WSJ, 11-10); "James Mackintosh | Nvidia CEO's Affair Should Ring Alarm Bells" (WSJ, 11-09); "Jensen Huang Betrayed the Leather Jacket Community" (NYT, 11-11); "Jensen Huang must resign" (Economist leader, 11-11).

**Where the negative tone sits.** It is densest in opinion, but it is also in news headlines. Loaded straight-news examples:

- "Nvidia CEO's Sudden Downfall Creates Nightmare for White House" (WSJ, 11-11)
- "How Jensen Huang's Affair Spiraled Into a National Security Nightmare" (WSJ, 11-10)
- "Commerce Dept. Chip Inquiry Was Halted After Nvidia Intervention" (NYT, 11-09)
- "Rubio Warned Officials About Nvidia Chief's Entanglement With Chinese Spy" (NYT, 11-08)
- "U.S. Cleared Nvidia Chips to Chinese Firms With Empty Offices and Troubling Ties" (NYT, 11-07)

**Several loaded words are not hostile.** "Betrayed" heads a humour piece. "Caper" heads a piece urging restraint before judging Beijing's motives. "Temptation" and "Only Human" head pieces that humanise Huang. Scoring these four as hostile would be an error.

## 2. Loaded wording, personalisation, gender, family

**Emotive words in the scandal period:** Nightmare ×4 (all WSJ), Scandal ×9, Affair ×18, and once or twice each Downfall, Spiraled, Rocks, Rattles, Plunge, Plummet, Slump, Vacuum, Terrible Timing, Drama, Can't Stop Selling, Honeypot, Temptation, Caper, Betrayed, Entanglement.

**Emotive wording was house style before 29 Oct, both ways.** Positive: "Blistering Chip Sales" (WSJ, 05-20), "Blockbuster" (WSJ, 05-15), "Blowout Second Quarter" (WSJ, 08-26), "Nvidia is driving the AI boom. Good" (Economist, 09-03). Negative: "Phantom Value" (WSJ, 09-29), "Ballooning" (WSJ, 08-26), "Nvidia Fatigue" (WSJ, 05-15). A crude keyword count gives 5 negative and 15 positive emotive hits in 68 pre-29-Oct headlines, against 66 negative and 10 positive in 100 later ones. Much of the later count is the factual nouns "affair" and "spy".

**Moral language.**

- "Jensen Huang Apologized to Nvidia for His Infidelity. His Kids Are on Staff." (WSJ, 11-09): two separate facts placed side by side imply nepotism.
- "Is Jensen Huang Too Powerful to Be Punished by Nvidia?" (NYT, 11-09): the question presupposes punishment is due.
- "Jensen Huang must resign" (Economist, 11-11): labelled advocacy.

**Framing of Alice Huang.** She is named in one headline: "Trump Says Nvidia CEO Didn't Know Alice Huang Was a Suspected Spy" (WSJ, 11-09). Elsewhere she is "Chinese Woman" ("The Chinese Woman at the Center of a Spy Probe After an Affair With Jensen Huang", WSJ, 11-09; "Nvidia Chief Told Trump He Did Not Know Chinese Woman Was Suspected Spy", NYT, 11-09), "Woman" ("The Woman in the Middle of Nvidia's Spy Scandal", NYT, 11-10), or a sexualised term ("Honeypot", "Temptation"; summary lines also used "honeytrap" and "lover"). Early reports used her professional title ("Chinese Executive Close to Nvidia CEO...", WSJ, 10-31; "...Affair With Chinese Executive", NYT, 11-10). The professional framing gave way to "woman" and sexual framing as volume grew, in news and podcast headlines as well as opinion.

**Family.** "...His Kids Are on Staff." (WSJ, 11-09); "Jensen Huang's Affair Puts His Wife in the Spotlight" (NYT, 11-11); "Could Jensen Huang's Family Take Over Nvidia?" (NYT, 11-11). Partly news-relevant (succession and nepotism are governance questions), but it widens the story's reach.

**The same event in different words:**

| Event | Neutral-ish | Loaded |
|---|---|---|
| Huang's 8 Nov acknowledgement | "Nvidia CEO Discloses Affair, Board Launches Probe..." (WSJ) | "...Apologized ... for His Infidelity" (WSJ) |
| 9 Nov share fall (4.3% per a WSJ recap) | "Nvidia Stock Drops Even as Broader Market Rallies" (NYT); "Nvidia Stock Slides After Chip Maker Opens Probe" (WSJ) | "Nvidia Shares Plunge After Chipmaker Opens Probe" (WSJ) |
| ~8% after-hours fall | "Nvidia Stock Falls Afterhours on Possible Jensen Huang Exit" (WSJ) | "Nvidia Shares Plummet as Board Is Said to Consider C.E.O.'s Future" (NYT) |
| One WSJ story, two titles | "How Nvidia CEO's Affair Became a National Concern" (11-11) | "How Nvidia CEO's Affair Became a National Security Nightmare" (11-10) |

## 3. Hedging versus assertion

Of 25 scandal headlines that mention spying, 10 carry an explicit hedge: "Seen as" (NYT, 10-29), "Suspected" (NYT 11-08; WSJ and NYT 11-09; WSJ 11-11), "Reports" (WSJ, 11-09), "Said to" (NYT, 11-11), "Seemingly" (WSJ, 11-09). Most unhedged ones use "spy" as a label for the story ("Spy Probe", "Spy Scandal"), not a claim about her.

**Headlines more certain than their own summary line** (paraphrased):

- "China's Top Spy Agency Recruited Woman Who Targeted Jensen Huang" (NYT, 11-06): the summary attributes the claim to an intelligence memo.
- "Rubio Warned Officials About Nvidia Chief's Entanglement With Chinese Spy" (NYT, 11-08): the summary describes her as linked to Chinese intelligence, not as a spy.
- "Despite Denial, Trump Was Told on Trip to China About Spying on Nvidia Leader" (NYT, 11-10): the summary says she is believed to be a spy.
- "Nvidia Gets a Chinese Honeypot Lesson" (WSJ opinion, 11-09): the summary calls her an alleged spy.
- "Commerce Dept. Chip Inquiry Was Halted After Nvidia Intervention" (NYT, 11-09): the summary says the inquiry was moved to the Justice Department after an Nvidia executive made contact. "Halted" is stronger than "moved", and "After" suggests causation.

**A prediction stated as fact.** "Nvidia CEO's Sudden Downfall Creates Nightmare for White House" (WSJ, 11-11). The same day WSJ headlines were hedged: "Possible Jensen Huang Exit", "Board Considers Ousting CEO", "Huang Might Need to Step Down ... Baird Says". The day before it ran "Bettors Assign Low Odds to Huang's Removal as Nvidia CEO".

**The reverse, headline less certain than its summary:** "Nvidia Chief Seen as Target of Chinese Spy Plot" (NYT, 10-29) and "Nvidia Stock Falls Afterhours on Possible Jensen Huang Exit" (WSJ, 11-11).

**Outlet consistency.** WSJ news headlines are consistently hedged. NYT news headlines are inconsistent: four use "Suspected", three state her status flatly, attributing it to U.S. intelligence in the summary line.

## 4. Escalation and repetition

| Date | NYT | WSJ | Econ |
|---|---|---|---|
| 10-29 (NYT scoop) | 1 | 0 | 0 |
| 10-31 to 11-07 | 4 | 3 | 0 |
| 11-08 (Huang acknowledges) | 3 | 0 | 0 |
| 11-09 | 9 | 26 | 1 |
| 11-10 | 8 | 21 | 1 |
| 11-11 | 9 | 14 | 1 |

Of WSJ's 61 items on 9 to 11 Nov: 21 live-blog cards, 9 podcasts or videos, 8 newsletter roundups, 4 opinion, 5 analysis, 14 standalone news articles. On 9 Nov alone eight WSJ headlines repeat the share fall ("Slides", "Slide", "Slump", "Plunge", "Decline an Outlier", "Slump Worst Since 2019", "Selloff, by the Numbers", a "Stocks to Watch" recap). Two argue the opposite: "Investors Brush Off ... Even Nvidia's Spy Scandal" and "Some Say Nvidia Chief's Affair Won't Affect Stock in the Long Run".

**The same machinery ran for good news.** Hugging Face deal, 3 Sep: five near-identical WSJ headlines in one day. Earnings, 26 to 27 Aug: nine WSJ items with mixed tone. NYT, the clean comparison, ran 2 items for earnings, 1 for Hugging Face, and 8 to 9 a day on 9 to 11 Nov.

**Does volume amplify negativity?** Mechanically, yes: a WSJ reader on 9 Nov meets the share fall in eight phrasings. But the same treatment was given to positive events, so volume reflects news value plus format multiplication, not targeting.

## 5. Cross-outlet convergence and outlet tilts

- Generic explainers: "What to Know About Nvidia's Investigation of Its C.E.O." (NYT, 11-08) and "What to Know About Nvidia's Investigation After CEO's Affair" (WSJ, 11-09).
- Indispensability, same day in all three: "How Indispensable Is Jensen Huang?" (NYT), "What Is Jensen Huang Worth to Nvidia?" (WSJ), "Can Nvidia's boss survive a Chinese-spy controversy?" (Economist), all 11-09.
- Governance within 24 hours: "Is Jensen Huang Too Powerful to Be Punished by Nvidia?" (NYT, 11-09), "Nvidia's Board Has a History of Letting Jensen Huang Get His Way" (NYT, 11-10), "A Spy Scandal Lays Bare Nvidia's Governance Vacuum" (WSJ, 11-10).
- The short seller: WSJ first ("The Short Seller That Seemingly Caught Onto Nvidia Chief's Affair Months Ago", 11-09), NYT two days later ("This Trader Raised Alarm About Nvidia's China Entanglements Months Ago", 11-11). Both draw on a public research report.

**Likely explanation:** shared obvious angles and two rival papers trading scoops. NYT had 10-29, 11-06, 11-08, 11-09, 11-10 and 11-11; WSJ had 10-31 and 11-11. Exact shared wording is rare. The core allegation traces to a memo circulated among U.S. officials, a common official source. Nothing in the headlines shows copying or coordination.

**Tilts.** NYT leans toward accountability for the Trump administration ("Rubio Warned...", "Despite Denial, Trump Was Told...", "Commerce Dept. Chip Inquiry Was Halted...", "Trump Officials Clashed..."). WSJ leans toward markets and governance; its opinion pages are split ("Honeypot Lesson" is hostile; "Caper", "Only Human" and "Temptation" are sympathetic) and it carries the most pro-Huang items ("Why Nvidia CEO Jensen Huang Is Unique", "A Reined In Jensen Huang Is Nvidia's Best Option"). The Economist moved furthest, from the leader "Nvidia is driving the AI boom. Good" (09-03) to the leader "Jensen Huang must resign" (11-11), both open advocacy.

## 6. The 15 most negative-sounding headlines: fact or wording?

| # | Headline (outlet, date) | Carried by | Neutral rewrite |
|---|---|---|---|
| 1 | "Nvidia CEO's Sudden Downfall Creates Nightmare for White House" (WSJ, 11-11) | Wording: asserts an outcome the outlet called only possible that day | "Possible Huang Exit Poses Problem for White House" |
| 2 | "How Jensen Huang's Affair Spiraled Into a National Security Nightmare" (WSJ, 11-10) | Mixed: facts plus "Spiraled", "Nightmare" | "How Jensen Huang's Affair Became a National-Security Concern" (WSJ's own retitle) |
| 3 | "Nvidia Gets a Chinese Honeypot Lesson" (WSJ opinion, 11-09) | Wording: sexualised term, more certain than its summary | "Huang's Affair With Alleged Chinese Agent Holds Security Lessons" |
| 4 | "Jensen Huang Betrayed the Leather Jacket Community" (NYT opinion, 11-11) | Wording (satire) | "A Humorist on Huang and the Leather Jacket" |
| 5 | "The Temptation of Jensen Huang" (WSJ opinion, 11-10) | Wording: casts the woman as temptation; piece is sympathetic | "Silicon Valley CEOs Face the Same Failings as Anyone" |
| 6 | "China's Jensen Huang Caper" (WSJ opinion, 11-10) | Wording: trivialising word in a cautionary piece | "What Would Beijing Gain From Targeting Jensen Huang?" |
| 7 | "Jensen Huang must resign" (Economist leader, 11-11) | Opinion on facts; labelled advocacy | "The Economist Argues Huang Should Step Down" |
| 8 | "Jensen Huang Apologized to Nvidia for His Infidelity. His Kids Are on Staff." (WSJ, 11-09) | Wording and juxtaposition | "Huang Apologizes to Staff; His Children Hold Senior Nvidia Roles" |
| 9 | "Nvidia Shares Plunge After Chipmaker Opens Probe" (WSJ, 11-09) | Mostly wording: the fall was 4.3% | "Nvidia Shares Fall 4% After Board Opens Probe" |
| 10 | "Nvidia Shares Plummet as Board Is Said to Consider C.E.O.'s Future" (NYT, 11-11) | Mostly fact (8% after hours, hedged) | "Nvidia Shares Fall 8% After Hours on Report Board Is Weighing C.E.O.'s Future" |
| 11 | "Investors Can't Stop Selling Nvidia Stock" (WSJ, 11-10) | Wording: hyperbole, at odds with WSJ's same-day morning note that the stock steadied | "Nvidia Shares Extend Decline" |
| 12 | "A Spy Scandal Lays Bare Nvidia's Governance Vacuum" (WSJ, 11-10) | Mostly fact (no chairman, no named successor); "Vacuum" is evaluative | "Scandal Highlights Nvidia's Lack of a Chairman and Succession Plan" |
| 13 | "Is Jensen Huang Too Powerful to Be Punished by Nvidia?" (NYT, 11-09) | Wording: presupposes guilt | "Huang's Grip on Nvidia Complicates Board Inquiry" |
| 14 | "China's Top Spy Agency Recruited Woman Who Targeted Jensen Huang" (NYT, 11-06) | Fact asserted beyond its sourcing | "U.S. Memo Says China's Spy Agency Recruited Executive Close to Huang" |
| 15 | "Commerce Dept. Chip Inquiry Was Halted After Nvidia Intervention" (NYT, 11-09) | Wording: "Halted" for "moved", implied causation | "Commerce Chip Inquiry Moved to Justice Dept. After Nvidia Executive Contacted Officials" |

Tally: 4 carried mainly by facts (7, 10, 12, 14), 2 mixed (2, 8), 9 mainly by word choice (1, 3, 4, 5, 6, 9, 11, 13, 15). Five of the nine are opinion, satire or question headlines.

## 7. Other anomalies

**Headlines rewritten after publication** (URL slug differs from the current headline): "Apple Loses Stock-Market Crown to Nvidia After Earnings" (WSJ, 11-03, slug says Apple "set to lose"); "Microsoft Falls Short of Surpassing Nvidia in Market Value" (WSJ, 11-10, slug says Microsoft "on pace to surpass"); "U.S. Stocks Leap Despite Nvidia Slide" (WSJ, 11-09); "Jensen Huang Affair Strains Taiwan's Devotion to Its Hometown Hero" (WSJ, 11-11); "How Nvidia CEO's Affair Became a National Concern" (WSJ, 11-11, slug says "national security nightmare"). The visible rewrites follow events or soften wording. None sharpens it.

**One piece counted twice.** "Risk Report: Nvidia's Succession Planning Is Big Risk" (WSJ, 11-10) reuses the slug of "Jensen Huang Doesn't Believe in Succession Planning. It's Become a Big Risk for Nvidia." (11-09).

**Checkable claims.** "One Great Chart: Nvidia Slump Worst Since 2019" (WSJ, 11-09) is hard to square with Nvidia's roughly 17% one-day fall on 27 January 2025; it may use a different measure. "Jensen Huang Investigation Rocks Nvidia as Board Investigates" (WSJ, 11-09) is tautological.

**Date anomalies.** Huang's acknowledgement was on Sunday 8 Nov; NYT dates it 11-08, WSJ's versions are dated 11-09. Both outlets date the ~8% after-hours fall to 11-11. These may be time-zone or update-time artifacts; timestamps would settle it.

**Packaging.** Question headlines ("Is ... Too Powerful to Be Punished", "How Indispensable", "What Does Beijing Know", "Could Jensen Huang's Family Take Over Nvidia?"), "Everything You Need to Know", and dramatised podcast titles ("Secrets, Chips and Spycraft: The Nvidia C.E.O. Scandal"). Standard podcast and video packaging at both papers.

**The baseline before 29 Oct was neutral to positive, not uncritical.** It included "Minicomputers Made by Nvidia Are Powering Moscow's A.I. Drones" (NYT, 08-24), "Regulators Are Investigating Nvidia's Licensing Deal With Groq" (NYT, 09-09), "Chinese Military Sought Nvidia Chips for Years, Report Says" (NYT, 06-01) and "How Nvidia's Buyback Created Phantom Value" (WSJ, 09-29).

**The framing follows the revelations.** Huang is first framed as a target ("Seen as Target", 10-29; "Woman Who Targeted Jensen Huang", 11-06; "Reports That CEO Was Spying Target", 11-09), then as culpable ("Infidelity", "Punished", "must resign", "Downfall", 11-09 to 11-11). The turn follows new facts: his own admission (11-08), reporting that an earlier denial was false (11-10), and a reported second relationship with a subordinate (NYT, 11-11, hedged "Said to").

## 8. Verdict

**What the data shows.** The tone turned sharply negative after 29 Oct. Loaded wording is concentrated in opinion (6 of 7) but appears in about a quarter of straight-news headlines. There are specific, checkable lapses: unhedged spy claims more certain than their summaries (NYT 11-06, 11-08, 11-10), "Halted" for "moved" (NYT 11-09), "Downfall" stated as fact (WSJ 11-11), "Plunge" for 4.3% (WSJ). Alice Huang is reduced to "woman" or sexualised terms more often than she is called an executive. WSJ's format machinery repeats the same negative fact many times a day.

**What the data does not show.** Intent, coordination or editorial motive, which headlines cannot reveal. A one-directional campaign: defensive headlines run throughout ("Investors Brush Off...", "Bettors Assign Low Odds...", "Tech Allies Rally Behind Jensen Huang...", "Why Nvidia CEO Jensen Huang Is Unique", "Jensen Huang Is Only Human"). Rewrites that sharpen tone. Repetition unique to the scandal.

**Verdict: no evidence of deliberate negative framing.** The tone is mostly explained by the news itself: an admitted affair with a person U.S. officials believe is a Chinese intelligence asset, a board investigation, an outside law firm, an 8% share fall, reported board deliberations on his future, and a reported second workplace relationship. On top of that sits ordinary headline craft (intensified market verbs, gendered shorthand, dramatised podcast titles) and competitive scoop volume. There are clear unfair framing choices, listed above, scattered across both papers alongside counter-framing.

**Confidence:** about 75% that the overall tone is explained by news value plus house style. Headlines cannot rule intent in or out.

**Strongest counter-argument.** Every lapse found points the same way. The unhedged spy claims, "Downfall", "Halted", "Plunge", "Infidelity ... His Kids Are on Staff" and the sexualised labels all make Huang look worse, and none errs in his favour. At dozens of headlines a day, accurate negative facts can be turned into a story of collapse before the board has acted. That is the best case for a systematic negative skew in headline craft, even without intent.
