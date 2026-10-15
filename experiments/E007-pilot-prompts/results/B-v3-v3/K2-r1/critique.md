CHART CHECK: Two panels of bar charts — left shows total crashes per weekday with count and % labels, right shows crashes per occurrence of that weekday; y-axes are labelled with units and start at 0, nothing is cut off or overlapping, and every plotted label matches values.csv (304,518/14.3% … 257,544/12.1%; 449, 462, 458, 470, 500, 425, 380). Shares sum to 100%, n = 2,132,218 matches the sum of the seven counts, n_days sums to 4,748 days (2013-01-01 to 2025-12-31), and all avg_crashes_per_day values recompute correctly.

ISSUES:
1. Written answer, sentence listing the ranking: "Thu next (318,376; 470/day), then Wed (311,111), Tue (313,488)" presents the days in descending order, but Tue (313,488) is larger than Wed (311,111). The descending order is Fri (338,800), Thu (318,376), Tue (313,488), Wed (311,111), Mon (304,518). Relatedly, "a steady build to Friday" glosses over Wed dipping below Tue, which the plotted values show.

UNVERIFIED:
- Whether the underlying parquet actually produces these per-day counts, n_days (678/679) and totals — only arithmetic on the reported values can be checked here.
- Whether the date filter and weekday extraction behave correctly for all rows (e.g., null crash_dates, out-of-range dates), which would require running the code.