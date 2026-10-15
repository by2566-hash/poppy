CHART CHECK: Bar chart with Year (2013–2025) on x-axis, "Pedestrians killed" (0–200) on y-axis, clear title, no legend needed, nothing cut off or overlapping; all 13 bar labels match values.csv exactly (176, 133, 133, 149, 127, 123, 131, 101, 132, 135, 107, 124, 119).

ISSUES: NONE

UNVERIFIED:
- Whether the crash data actually covers all of 2025 (the printed MIN/MAX crash_date output isn't shown); if 2025 is a partial year, the 119 value and the 2013→2025 decline would be comparing unequal periods.
- Whether the yearly sums match the underlying parquet data (would require reading the data file). Arithmetic in the written answer checks out from the shown values: total 1,690, average 130.0, min 101 (2020), max 176 (2013).