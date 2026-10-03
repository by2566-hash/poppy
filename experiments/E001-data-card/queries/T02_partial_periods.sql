WITH date_bounds AS (
  SELECT min(crash_date) AS first_date, max(crash_date) AS last_date
  FROM read_parquet('data/processed/nyc_crashes.parquet')
)
SELECT year(crash_date) AS year, month(crash_date) AS month, count(*) AS crashes,
  date_bounds.first_date, date_bounds.last_date
FROM read_parquet('data/processed/nyc_crashes.parquet')
 CROSS JOIN date_bounds
WHERE year(crash_date) IN (2012, 2026)
GROUP BY 1,2,4,5 ORDER BY 1,2;
