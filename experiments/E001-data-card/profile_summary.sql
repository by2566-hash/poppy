SELECT count(*) AS row_count,
  min(crash_date) AS first_date,
  max(crash_date) AS last_date,
  count(DISTINCT crash_date) AS distinct_crash_dates,
  count(DISTINCT collision_id) AS distinct_collision_ids,
  count(*) FILTER (WHERE crash_date IS NULL) AS null_crash_dates
FROM read_parquet('data/processed/nyc_crashes.parquet');
