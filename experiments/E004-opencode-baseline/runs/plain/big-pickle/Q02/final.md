I'll start by reading the dataset documentation and exploring the data.

Data covers 2012-07 to 2026-06. Let me check for structural breaks before drawing any conclusions.

Raw counts point one way, but "safety" means risk per trip — and exposure isn't in this dataset. Let me dig deeper internally and get the denominator separately.

Important external context found. Now let me fix my bike-detection query and test whether I can split traditional bikes from e-bikes.

Now the statistical treatment — testing whether the year-to-year swings are even real.

I have NYC DOT's official ridership series — that's the denominator I need. Let me compute exposure-adjusted rates.

Clear picture now. Let me build the charts.

I can't view images directly, so let me verify the outputs programmatically and confirm the plotted values.

## Short answer: partly — and definitely not the way the raw data implies.

The honest read is **"somewhat, on a per-trip basis, but not on a per-death basis."** The raw counts alone would tell you the opposite, which is the trap here.

**Charts:** `out/cyclist_safety.png` (4-panel), `out/cyclist_safety_composition.png`

### What the raw data says: cyclists got *worse*
| | 2013–2016 | 2021–2023 |
|---|---|---|
| Cyclist deaths | 64 | 69 |
| Cyclist share of road deaths | 6.1% | 8.5% |

Cyclist deaths have been flat-but-terrifyingly-noisy for 13 years — 10 (2018) then 31 (2019) then 29 (2020). With ~20 events a year, Poisson noise alone spans roughly 11–34, so single years are close to meaningless (10 vs 31 is p=0.001; 19 vs 31 is p=0.12).

### Three reasons the raw trend misleads

**1. Exposure grew much faster than casualties.** NYC bike trips rose 64% (380k → 620k/day, DOT *Cycling in the City*). Dividing by trips:

| Per 100M bike trips, 2013-16 → 2021-23 | Rate ratio | 95% CI | p |
|---|---|---|---|
| Cyclist deaths | 1.04 | 0.74–1.46 | 0.73 — flat |
| Cyclist injuries | **0.84** | 0.82–0.86 | <0.001 — **down 16%** |
| All cyclist casualties | **0.84** | 0.82–0.86 | <0.001 — **down 16%** |

Casualty rate fell 2,946 → 2,302 per 100M trips (−22% on endpoints). DOT's own *Cycling Risk Indicator* — which counts serious injuries, not scrapes — puts the long-run decline at ~34 → 16 per 10M rides (−53%).

**2. The rising cyclist share is a denominator effect.** Pedestrian deaths fell 591 → 374 (−37%) over the same span. Cyclists lost share of a shrinking pie, not because they got worse.

**3. "Cyclist deaths up" is almost entirely e-bikes.** NYPD began folding e-bikes into the cyclist category around 2020. Splitting them out (DOT's published mode data): traditional-bike deaths fell **24 → 7** (2017→2024, −71%) while e-bike deaths rose 2 → 17–23. E-bikes are the one genuinely deteriorating segment, and they're a different risk profile (heavier, faster, 20+ mph).

### One caveat that undercuts everything
The 60% crash-count drop (231k in 2018 → 86k in 2025) is **mostly a reporting change, not safety**. Crashes with no injury fell from 78.5% to 56.3% of the total; injury crashes only fell 45,439 → 37,420 (−18%). I therefore used person casualties, not crash counts, throughout.

### Limits of this analysis
- 2026 excluded (partial, through Jun 11); 2012 excluded (starts Jul 1); 2020 is a COVID structural break.
- My own e-bike split from `vehicle_type_code` recovered only ~half of DOT's e-bike deaths, so I used DOT's official split for panel (a).
- No injury-severity field, so I can't reproduce DOT's KSI metric — only the all-injury rate, which is noisier and more conservative.
- The trip denominator is an ACS-commuter extrapolation, not a count; it also can't separate traditional from e-bike trips, which is exactly the split that matters most.
- `number_of_persons_killed` exceeds the sum of mode-specific deaths by 2–4% from 2021 (NYPD added motorized two-wheeler categories).

**Bottom line:** riding a bike in NYC is meaningfully safer per trip than in 2013 — mostly via fewer injuries, and dramatically so if you're on a traditional bike. But per-trip *death* risk is statistically flat, and if you're on an e-bike it's probably gotten worse. Anyone quoting raw cyclist death counts is measuring e-bike adoption, not safety.