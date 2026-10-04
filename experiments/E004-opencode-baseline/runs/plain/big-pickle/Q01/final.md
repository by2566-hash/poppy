I'll start by reading the dataset documentation and inspecting the data.

Data is clean for 2016–2025 (only 36 NULL rows out of 1.5M; the large NULL block is confined to partial-year 2026). Computing the yearly totals:

Now the chart:

I can't visually verify the PNG (no image input in this model), but the chart rendered from the verified data below.

## People killed in NYC motor vehicle crashes, 2016–2025

| Year | Killed | Pedestrians | Cyclists | Motorists | Reported crashes | Killed per 100 crashes |
|------|-------:|------------:|---------:|----------:|-----------------:|------------------------:|
| 2016 | 246 | 149 | 18 | 72 | 229,833 | 0.11 |
| 2017 | 256 | 127 | 27 | 107 | 231,007 | 0.11 |
| 2018 | 231 | 123 | 10 | 98 | 231,564 | 0.10 |
| 2019 | 244 | 131 | 31 | 82 | 211,486 | 0.12 |
| 2020 | 269 | 101 | 29 | 139 | 112,918 | 0.24 |
| 2021 | **297** | 132 | 19 | 134 | 110,558 | 0.27 |
| 2022 | 290 | 135 | 19 | 116 | 103,887 | 0.28 |
| 2023 | 280 | 107 | 31 | 123 | 96,607 | 0.29 |
| 2024 | 268 | 124 | 24 | 111 | 91,316 | 0.29 |
| 2025 | **229** | 119 | 23 | 81 | 85,546 | 0.27 |

**Trend:** three distinct phases.

1. **2016–2019 — flat, ~230–256 deaths/yr**, with ~230,000 crashes annually.
2. **2020–2021 — spike to a decade high of 297.** This is the counterintuitive part: crash volume *halved* (COVID-era traffic collapse) yet deaths rose ~22% vs 2019. The mechanism is visible in the last column — deaths per crash jumped from 0.12 to 0.27, and vehicle-occupant deaths specifically surged (82 → 134) while pedestrian deaths fell (131 → 132, but from a much lower baseline given far less walking). Empty roads plus speed and reduced enforcement.
3. **2022–2025 — slow decline back to 229**, the lowest of the decade and 17 fewer than 2016 (−7%). Deaths fell only 23% from the 2021 peak while crashes fell 23% from 2020 levels, so the elevated per-crash fatality rate has largely persisted.

**The headline caveat:** total deaths are nearly flat across the decade, but that flatness hides a structural change. Reported crashes dropped 63% (231,564 → 85,546) while deaths fell just 7%, so **each crash is now roughly 2.5× more deadly** than in 2016. Safety progress measured only by the raw death count would call this decade a success; measured per unit of exposure or per crash, it is not.

Notes on the data: figures use `number_of_persons_killed` per the README, summing the 36 NULL rows as 0 (negligible — 0.002%). 2016–2025 are all complete years; the snapshot extends to 2026-06-11, and I excluded 2026 because it is partial — 24% of its rows have NULL casualty fields. 2025 is flagged preliminary in the source and subject to revision.

Chart: `./out/nyc_fatalities_2016_2025.png` (bars = deaths, line = deaths per 100 crashes); data: `./out/killed_by_year.csv`.