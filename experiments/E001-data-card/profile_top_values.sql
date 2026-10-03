WITH crashes AS (SELECT * FROM read_parquet('data/processed/nyc_crashes.parquet'))
SELECT 'borough' AS column_name, coalesce(cast(borough AS VARCHAR),'[NULL]') AS value, count(*) AS occurrences, round(100.0*count(*)/sum(count(*)) OVER (PARTITION BY 'borough'),4) AS pct FROM crashes GROUP BY 1,2 QUALIFY row_number() OVER (PARTITION BY 'borough' ORDER BY count(*) DESC, value) <= 25
UNION ALL
SELECT 'contributing_factor_vehicle_1' AS column_name, coalesce(cast(contributing_factor_vehicle_1 AS VARCHAR),'[NULL]') AS value, count(*) AS occurrences, round(100.0*count(*)/sum(count(*)) OVER (PARTITION BY 'contributing_factor_vehicle_1'),4) AS pct FROM crashes GROUP BY 1,2 QUALIFY row_number() OVER (PARTITION BY 'contributing_factor_vehicle_1' ORDER BY count(*) DESC, value) <= 25
UNION ALL
SELECT 'vehicle_type_code1' AS column_name, coalesce(cast(vehicle_type_code1 AS VARCHAR),'[NULL]') AS value, count(*) AS occurrences, round(100.0*count(*)/sum(count(*)) OVER (PARTITION BY 'vehicle_type_code1'),4) AS pct FROM crashes GROUP BY 1,2 QUALIFY row_number() OVER (PARTITION BY 'vehicle_type_code1' ORDER BY count(*) DESC, value) <= 25
ORDER BY column_name, occurrences DESC, value;
