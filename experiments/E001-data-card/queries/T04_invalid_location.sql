SELECT year(crash_date) AS year, count(*) AS crashes,
  count(*) FILTER (WHERE latitude IS NULL) AS null_latitude,
  count(*) FILTER (WHERE longitude IS NULL) AS null_longitude,
  count(*) FILTER (WHERE latitude IS NULL OR longitude IS NULL) AS either_coordinate_null,
  count(*) FILTER (WHERE latitude=0 OR longitude=0) AS zero_coordinate,
  count(*) FILTER (WHERE (latitude IS NOT NULL AND latitude<>0 AND (latitude<=40.4 OR latitude>=41.0)) OR (longitude IS NOT NULL AND longitude<>0 AND (longitude<=-74.3 OR longitude>=-73.6))) AS outside_rough_bounds,
  round(100.0 * count(*) FILTER (WHERE latitude IS NULL OR longitude IS NULL) / count(*), 4) AS either_null_pct,
  round(100.0 * count(*) FILTER (WHERE latitude=0 OR longitude=0) / count(*), 4) AS zero_coordinate_pct,
  round(100.0 * count(*) FILTER (WHERE (latitude IS NOT NULL AND latitude<>0 AND (latitude<=40.4 OR latitude>=41.0)) OR (longitude IS NOT NULL AND longitude<>0 AND (longitude<=-74.3 OR longitude>=-73.6))) / count(*), 4) AS outside_bounds_pct
FROM read_parquet('data/processed/nyc_crashes.parquet') GROUP BY 1 ORDER BY 1;
