SELECT year(crash_date) AS year, count(*) AS crashes,
  count(*) FILTER (WHERE borough IS NULL OR trim(borough)='') AS missing_borough,
  round(100.0 * count(*) FILTER (WHERE borough IS NULL OR trim(borough)='') / count(*), 4) AS missing_pct
FROM read_parquet('data/processed/nyc_crashes.parquet')
GROUP BY 1 ORDER BY 1;
