I'll start by reading the dataset description and exploring the data.

Bash is restricted to certain patterns; I'll work through `python3`. Let me explore the data.

Data spans 2012-07 to 2026-06 (2.27M crashes), with partial months at both ends. Let me build the monthly series.

Clear pattern. Now let me quantify pre/post and examine severity, which is the crux of the question.

Total crashes fell but deaths didn't. Let me validate the exposure hypothesis internally and run a proper pre/post comparison.

Strong internal signal. Now the formal pre/post comparison.

Now let me build the chart.

I can't view images, so let me verify every number in the chart programmatically.

Several hardcoded annotations were wrong (monthly vs annual basis, and a noisy endpoint month). Let me fix by deriving every number from the plotted series and using 12-month rolling means.

Now I have correct figures. Let me rewrite the chart deriving all labels from data.

Index is month-start; my labels used month-end. Fixing.

All figures now derive from data. One issue: in panel C the two lines nearly coincide (73.6 vs 72), so one would hide the other. Let me restructure it to show the actual risk shift.

Important correction: motorist harm per crash also doubled (217→395 per 1k). So the story is a *composition* shift, not just an exposure one. Let me restructure panel C to show that cleanly.

Now the panel C rebuild:

Let me add explicit y-limits to prevent annotation collisions, then do a final render check.

Chart written to `./out/crashes_covid.png` (2640×1720). I can't view images in this session, so I verified every number in the figure programmatically instead of by eye.

## Short answer: yes, but the headline number is misleading

Monthly averages, pre-COVID (Feb 2018–Feb 2020, 26 mo) vs. post (Jan 2022–May 2026, 53 mo):

| | Pre-COVID | Post-COVID | Change |
|---|---|---|---|
| Crashes | 18,043/mo | 7,763/mo | **−57%** |
| Persons injured | 4,758/mo | 4,320/mo | **−9%** |
| Persons killed | 21.3/mo | 21.4/mo | **unchanged** |
| Ped+cyclist injuries | 1,296/mo | 1,207/mo | −7% |

**The timeline:** crashes bottomed at 4,129 in April 2020 (−77% vs. the pre-COVID average), partially rebounded through 2021, then kept sliding — 2025 was 85,546 crashes, still ~60% below 2019. There was no return to pre-COVID levels.

**Why that drop isn't a safety gain:**
1. **Harm barely moved.** 57% fewer crashes yielded only 9% fewer injuries and zero change in deaths.
2. **Harm per crash roughly doubled.** Motorist injuries per 1,000 crashes: 217 → 397. Pedestrian+cyclist injuries per 1,000: 74 → 169.
3. **The mix shifted, it didn't just shrink.** Share of crashes injuring/killing a motorist went 14.4% → 26.0%; involving a pedestrian or cyclist, 7.2% → 16.5%. Both roughly doubled — most of the vanished crashes were low-speed property-damage fender-benders that stopped crossing the $1,000/injury reporting threshold.
4. **Exposure check:** crashes injuring a motorist (the category that scales with vehicle-miles) fell only ~26%, versus ~59% for all crashes. So the denominator isn't uniform across the mix.

**Caveats worth flagging:** crash count is a proxy for exposure and this dataset has no mileage field, so a true per-mile rate isn't computable here. The reportable threshold also means the count responds to *severity*, not just frequency — which is exactly what changed. NYPD data are preliminary. June 2026 is partial (data ends 06-11) and was excluded.

**Bottom line:** crashes did go down and stayed down, but that's a mix-and-exposure effect. Post-COVID NYC is safer by the fender-bender count, roughly no safer by the death count, and substantially less safe for pedestrians per crash.

One caveat on my own method: I used trailing-12-month means for panels B–D after finding single-month endpoints misleading — May 2026 had only 8 deaths, which alone would have implied a 62% drop.