I'll start by reading the dataset description and exploring the data.

Key finding already: 30% of rows have a **NULL borough**. Let me dig into whether that's random and check data integrity.

Crashes are down ~55% since 2016 but **deaths are flat/up**. Let me get defensible population denominators for a per-capita view.

Got Census Vintage 2024 (July 2024) borough populations from NYC DCP. Now the normalized analysis:

Answer genuinely flips by metric. Let me smooth the small-count noise with a 5-year window and build charts.

Now let me build the charts.

I can't view images (no image input support), so let me verify the charts structurally and independently double-check the headline numbers.

Both charts render correctly and the SQL cross-check matches the pandas path exactly.

## Brooklyn — but the answer flips depending on how you define "dangerous"

I used 2021–2025 (avg per year) with Census Vintage 2024 populations, since borough-normalized rates are the only fair comparison — raw counts just rank population size.

| Borough | Crashes /100k | Deaths /100k | Ped+cyclist deaths /100k | Deaths per 1k crashes |
|---|---|---|---|---|
| **Brooklyn** | **906** | **2.03** | 1.31 | 2.24 |
| Bronx | 816 | 1.95 | 0.92 | 2.39 |
| Queens | 790 | 1.57 | 0.88 | 1.99 |
| Manhattan | 727 | 1.70 | **1.34** | 2.34 |
| Staten Island | 545 | 1.41 | 0.72 | **2.58** |

Brooklyn leads on every volume and per-capita measure: ~35% of the city's crashes and deaths on ~31% of its population (risk index 1.13). But three lenses disagree:

- **Walking or cycling → Manhattan.** Highest pedestrian+cyclist death rate (1.34/100k), and 67% of its traffic deaths are pedestrians vs. 45% in the Bronx.
- **Severity per crash → Staten Island.** Fewest crashes, but the most lethal ones (2.58 deaths per 1,000 crashes, driven by high-speed arterial/expressway crashes).
- **As a driver → the Bronx.** Highest motorist death rate (0.88/100k), ~2.9× Manhattan.

## The finding I'd flag hardest

**Crashes and deaths have decoupled.** Since 2016 reported crashes fell 55.3% while deaths *rose* 21.5% (130 → 158/yr), so lethality per crash nearly tripled (0.85 → 2.31 per 1,000). Success on crash *counts* is not producing success on deaths.

## Data caveats that materially affect this

- **30% of rows (691k) have a NULL borough** — spread across all years (20–38%), not a recent pipeline break. This isn't random: those crashes are **~60% more likely to be fatal** (0.30% vs 0.17–0.23%), so every rate above modestly *understates* danger. I excluded them because imputing them would require an external crosswalk.
- **No exposure denominator.** Per-capita is a proxy; VMT or registered vehicles per borough would be better and would likely narrow Staten Island's apparent advantage.
- **Reporting threshold bias.** Reports require injury, death, or ≥$1,000 damage, so minor fender-benders are invisible — and that undercount likely varies by borough urbanity.

Charts: `out/borough_scorecard.png` (four ranking lenses), `out/borough_trend_risk.png` (trend + risk index). Script: `analysis.py`.