SELECT year(crash_date) AS year, count(*) AS crashes,
  count(*) FILTER (WHERE lower(trim(coalesce(contributing_factor_vehicle_1,'')))='unspecified') AS unspecified_count,
  count(*) FILTER (WHERE contributing_factor_vehicle_1 IS NULL OR trim(contributing_factor_vehicle_1)='') AS empty_count,
  round(100.0 * count(*) FILTER (WHERE lower(trim(coalesce(contributing_factor_vehicle_1,'')))='unspecified') / count(*), 4) AS unspecified_pct,
  round(100.0 * count(*) FILTER (WHERE contributing_factor_vehicle_1 IS NULL OR trim(contributing_factor_vehicle_1)='') / count(*), 4) AS empty_pct
FROM read_parquet('data/processed/nyc_crashes.parquet') GROUP BY 1 ORDER BY 1;
