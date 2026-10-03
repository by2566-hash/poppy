SELECT year(crash_date) AS year, sum(coalesce(number_of_persons_killed,0)) AS persons_killed
FROM read_parquet('data/processed/nyc_crashes.parquet')
WHERE crash_date >= DATE '2016-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1 ORDER BY 1;
