The parquet uses `number_of_motorist_killed` (singular), while the supplied schema description says `number_of_motorists_killed`. I’ve confirmed the actual field name from DuckDB’s binding error and am aligning both plans and checks to the file.
ANSWER:
- Motorist deaths exceeded cyclist deaths every year; in 2025 the counts were 81 versus 23, with period highs of 139 motorist deaths in 2020 and 31 cyclist deaths in both 2019 and 2023.
- Cyclists accounted for 9.1%–27.4% of annual motorist-plus-cyclist deaths, peaking at 27.4% in 2019; motorists made up the remainder.