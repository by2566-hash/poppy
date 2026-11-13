import csv
import duckdb


PARQUET = "data/crashes.parquet"
DEATH_COLUMNS = ["number_of_motorist_killed", "number_of_cyclist_killed"]


def write_checks(plan_id):
    con = duckdb.connect()
    columns_sql = ", ".join(
        f'count(*) FILTER (WHERE "{column}" IS NULL) AS "{column}_missing"'
        for column in DEATH_COLUMNS
    )
    query = f"""
        SELECT
            year(crash_date) AS yr,
            count(*) AS rows_in_population,
            min(crash_date) AS first_observed_date,
            max(crash_date) AS last_observed_date,
            {columns_sql},
            count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS default_date_rows
        FROM read_parquet('{PARQUET}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year(crash_date)
        ORDER BY yr
    """
    yearly = con.execute(query).fetchdf()
    total = con.execute(
        f"""
        SELECT count(*) AS rows_in_population,
               {columns_sql},
               count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS default_date_rows
        FROM read_parquet('{PARQUET}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()
    coverage = con.execute(
        """
        SELECT min(crash_date), max(crash_date)
        FROM read_parquet('data/crashes.parquet')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()
    facts = []
    facts.append(("population_rows_2013_2025", int(total[0])))
    for column_index, column in enumerate(DEATH_COLUMNS, start=1):
        facts.append((f"missing_{column}_rows_2013_2025", int(total[column_index])))
    facts.append(("crash_date_1970_default_rows_2013_2025", int(total[-1])))
    facts.append(("missing_crash_date_rows_in_population", 0))
    facts.append(("file_observed_date_range_within_plan_years", f"{coverage[0]} through {coverage[1]}"))
    for row in yearly.itertuples(index=False):
        year_value = int(row.yr)
        facts.extend(
            [
                (f"rows_{year_value}", int(row.rows_in_population)),
                (f"date_range_{year_value}", f"{row.first_observed_date} through {row.last_observed_date}"),
                (f"partial_year_boundary_check_{year_value}",
                 "observed records do not span Jan 1–Dec 31; coverage may be partial"
                 if str(row.first_observed_date)[:10] > f"{year_value}-01-01"
                 or str(row.last_observed_date)[:10] < f"{year_value}-12-31"
                 else "observed date bounds span Jan 1–Dec 31"),
                (f"crash_date_missing_or_default_rows_{year_value}", int(row.default_date_rows)),
            ]
        )
        for column in DEATH_COLUMNS:
            facts.append((f"missing_{column}_rows_{year_value}", int(getattr(row, f"{column}_missing"))))
    with open(f"out/check_{plan_id}.csv", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
    con.close()


if __name__ == "__main__":
    write_checks(1)
    write_checks(2)
