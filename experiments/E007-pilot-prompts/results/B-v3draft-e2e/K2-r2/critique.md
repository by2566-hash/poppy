CHART CHECK: Bar chart with x-axis "Day of week" (Mon–Sun), y-axis "Number of crashes" (0–400,000), weekday/weekend legend, total annotation 2,132,218, and per-bar labels showing count, % share, and per-day average; nothing is cut off or overlapping. Every label matches values.csv (counts identical, shares rounded to one decimal, avgs rounded to whole), and the seven counts sum to 2,132,218.

ISSUES:
1. Written answer: "about 32% fewer crashes on Sundays than Fridays" is wrong arithmetic. Friday − Sunday = 338,800 − 257,544 = 81,256, which is 24.0% of Friday's 338,800, so Sundays have about 24% fewer crashes than Fridays. (32% is roughly the reverse comparison: Fridays have ~31.5% more than Sundays; that is not what the sentence says.)
2. Written answer: "consistent with lighter traffic and fewer commuters on weekends" asserts a cause (traffic volume, commuter counts) that the allowed data (one row per crash) contains no variable for; it cannot support this explanation. Remove it or mark it explicitly as speculation.

UNVERIFIED:
- Whether ./data/crashes.parquet actually contains all crashes for 2013-01-01 through 2025-12-31 and whether the date filter excluded or included rows incorrectly (requires the data file).
- The crash counts themselves and the per-weekday occurrence counts (678/679) as computed from the data (calendar arithmetic is internally consistent: 2013-01-01 to 2025-12-31 = 4,748 days, with Tue and Wed occurring 679 times, matching values.csv).