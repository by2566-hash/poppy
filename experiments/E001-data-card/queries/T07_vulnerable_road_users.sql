SELECT year(crash_date) AS year,
  sum(coalesce(number_of_cyclist_injured,0)) AS cyclist_injured,
  sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_killed,
  sum(coalesce(number_of_pedestrians_injured,0)) AS pedestrian_injured,
  sum(coalesce(number_of_pedestrians_killed,0)) AS pedestrian_killed
FROM read_parquet('data/processed/nyc_crashes.parquet')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1 ORDER BY 1;
