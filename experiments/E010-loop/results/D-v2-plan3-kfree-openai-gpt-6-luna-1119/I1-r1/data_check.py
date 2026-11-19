import csv
import duckdb


DATA = "data/crashes.parquet"
YEARS = range(2013, 2026)

con = duckdb.connect()
query = """
    SELECT
        crash_date,
        number_of_motorist_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date <= DATE '2025-12-31'
"""
rows = con.execute(query, [DATA]).fetchdf()
rows["year"] = rows["crash_date"].dt.year

for plan_id in (1, 2):
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    add("candidate_population_rows_2013_2025", len(rows))
    add("source_schema_motorist_death_column", "number_of_motorist_killed (singular; differs from the supplied description)")
    add("crash_date_missing_rows_in_candidate_population", int(rows["crash_date"].isna().sum()))
    add(
        "number_of_motorist_killed_missing_rows_in_candidate_population",
        int(rows["number_of_motorist_killed"].isna().sum()),
    )

    for year in YEARS:
        subset = rows.loc[rows["year"] == year]
        eligible = subset.loc[subset["number_of_motorist_killed"].notna()]
        add(f"candidate_crash_rows_{year}", len(subset))
        add(f"usable_crash_rows_{year}_nonmissing_motorist_death_count", len(eligible))
        if subset.empty:
            add(f"date_coverage_{year}", "no rows")
        else:
            first = subset["crash_date"].min().date().isoformat()
            last = subset["crash_date"].max().date().isoformat()
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31"
            partial = first != year_start or last != year_end
            add(f"date_coverage_{year}", f"{first} through {last}; partial_year={str(partial).lower()}")

    with open(f"out/check_{plan_id}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
