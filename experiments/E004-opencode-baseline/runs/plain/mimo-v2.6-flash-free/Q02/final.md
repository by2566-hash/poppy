**Short answer: No — on every measure this dataset supports, NYC cyclists are worse off than a decade ago, and they're the only road user group that is.**

Data: `crashes.parquet`, 2012-07-01 → 2026-06-11 (2.27M crashes). Analysis uses complete years 2013–2025; charts in `./out/` (code: `analyze.py`).

### Head-to-head: 2013–19 average vs 2023–25 average

| Metric | 2013–19 | 2023–25 | Change |
|---|---|---|---|
| Cyclist injuries / yr | 4,562 | 5,229 | **+15%** |
| Cyclist deaths / yr | 18.9 | 26.0 | **+38%** |
| Pedestrian injuries / yr | 11,006 | 9,275 | −16% |
| Motorist injuries / yr | 41,825 | 36,251 | −13% |
| Cyclists' share of all injury victims | 7.9% | 10.3% | **+30%** |
| Cyclists' share of all road deaths | 7.4% | 10.5% | **+41%** |
| Deaths per 1,000 cyclist injuries | 4.1 | 5.0 | **+20%** |
| All injuries, all modes | 57,394 | 50,755 | −12% |

- **Relative:** cyclists went from ~8% to ~10% of everyone injured and from ~7% to ~10.5% of everyone killed, while pedestrian injuries/deaths fell ~16%.
- **Recent pace:** in the trailing 12 months (Jun 2025–Jun 2026) there were 5,414 cyclist injuries — **14.8/day vs 10.8/day in Jun 2013–Jun 2014 (+37%)**, with 26 deaths vs 15. Jan–Jun 2026 runs ~12.0/day, flat-to-slightly-down vs 2025 (12.3/day): the worsening is real but has plateaued since 2023.
- **Where:** all five boroughs worsened — Brooklyn +9% (1,426→1,553/yr), Queens +16%, Bronx +30%, Manhattan +33%, Staten Island +49% (tiny base, 40→59).
- Cyclist death *severity* (deaths per 1,000 injuries) also rose (4.1→5.0), though motorist severity rose more (2.3→2.9) and pedestrian severity was flat (~12.6).

### Two important caveats
1. **No exposure denominator.** This data has no trips/miles ridden, so I can't compute *risk per ride*. Cyclist injuries are up ~15% vs 2013–19 — if cycling volume grew faster than that (it plausibly did), per-trip risk could still have fallen while absolute harm rose. That's the one way the answer flips, and it can't be settled with this file alone.
2. **Don't use crash counts.** Reported crashes fell 211k (2019) → 86k (2025) purely because the share of crashes with nobody hurt dropped from 79% to 56% (`out/05_reporting_change.png`). Injury/fatality counts are mandatory reports and are the comparable series; I also skipped the free-text `vehicle_type` columns (garbage values, and 2026 values are truncated, e.g. "BICY").

**Bottom line:** while NYC got safer overall for pedestrians and motorists, cyclists moved in the opposite direction — more injuries, more deaths, a growing share of the city's road-death toll.