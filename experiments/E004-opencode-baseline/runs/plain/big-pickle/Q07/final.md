I'll start by reading the dataset documentation and exploring the data.

I can't visually inspect the PNG, so let me verify the underlying numbers programmatically.

## Driver Inattention/Distraction is the main cause

**462,105 crashes — 20.4% of all 2.27M crashes, and 30.7% of crashes where police recorded an actual cause.** It is roughly **3.4x** the next cause.

Ranking (primary vehicle factor, excluding "Unspecified"):

| # | Cause | Crashes | % of specified |
|---|---|---|---|
| 1 | **Driver Inattention/Distraction** | 462,105 | 30.7% |
| 2 | Failure to Yield Right-of-Way | 136,046 | 9.0% |
| 3 | Following Too Closely | 121,711 | 8.1% |
| 4 | Backing Unsafely | 82,577 | 5.5% |
| 5 | Other Vehicular | 71,429 | 4.7% |

The answer is robust to method: it ranks #1 both by primary factor (vehicle 1) and by counting a factor on *any* vehicle in the crash (489,682 crashes). Adding the narrower distraction codes (phone, texting, passenger, navigation, etc.) takes the distraction/inattention family to **32.4%** of specified-cause crashes. It's #1 in every borough (28–33%) and every year in the dataset.

**Three important caveats:**

1. **A third of crashes have no cause recorded.** `contributing_factor_vehicle_1` is "Unspecified" for 756,643 crashes (33.3%), concentrated in 2012–2015 (59% in 2012). NYPD reporting improved sharply around 2016. So 20.4% of *all* crashes understates the rate, and pre-2016 years are the weakest part of the data.

2. **Frequency ≠ severity.** Inattention dominates crash *counts*, but it's a low-severity cause: 27% of inattention crashes injure someone, versus 43% for Failure to Yield. For **fatal** crashes the picture inverts — Unsafe Speed (466 deaths), Failure to Yield (313), and Traffic Control Disregarded (307) all exceed Inattention (443). If you care about deaths rather than crash volume, speeding is the answer.

3. **Data quality.** `borough` is NULL for 691,375 rows (30%), and there are ~250 rows with junk numeric codes (`36`, `80`) in the factor columns, plus near-duplicate labels (`Illness`/`Illnes`, differing capitalization on `Cell Phone (hand-Held)`). None are large enough to change the ranking.

Chart saved to `./out/crash_causes.png` (3 panels: cause ranking, reporting-quality trend, deaths by cause).