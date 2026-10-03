WITH factors AS (
  SELECT 'all_crashes' AS scope, contributing_factor_vehicle_1 AS factor, count(*) AS crashes
  FROM read_parquet('data/processed/nyc_crashes.parquet')
  WHERE contributing_factor_vehicle_1 IS NOT NULL AND trim(contributing_factor_vehicle_1)<>''
    AND lower(trim(contributing_factor_vehicle_1))<>'unspecified'
  GROUP BY 1,2
  UNION ALL
  SELECT 'fatal_crashes' AS scope, contributing_factor_vehicle_1 AS factor, count(*) AS crashes
  FROM read_parquet('data/processed/nyc_crashes.parquet')
  WHERE coalesce(number_of_persons_killed,0)>=1 AND contributing_factor_vehicle_1 IS NOT NULL AND trim(contributing_factor_vehicle_1)<>''
    AND lower(trim(contributing_factor_vehicle_1))<>'unspecified'
  GROUP BY 1,2
)
SELECT scope, factor, crashes FROM factors
QUALIFY row_number() OVER (PARTITION BY scope ORDER BY crashes DESC, factor) <= 10
ORDER BY scope, crashes DESC, factor;
