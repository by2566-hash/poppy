WITH exploded AS (
  SELECT crash_date, trim(v.type_code) AS type_code
  FROM read_parquet('data/processed/nyc_crashes.parquet'),
  LATERAL (VALUES (vehicle_type_code1),(vehicle_type_code2),(vehicle_type_code3),(vehicle_type_code4),(vehicle_type_code5)) v(type_code)
  WHERE v.type_code IS NOT NULL AND trim(v.type_code)<>''
), matched AS (
  SELECT * FROM exploded
  WHERE regexp_matches(lower(type_code), '\be[- ]?b(?:ik(?:e)?)?\b|\bscoot\w*\b|\bmoped\b')
)
SELECT type_code, count(*) AS occurrences, min(year(crash_date)) AS first_year,
  sum(count(*)) OVER () AS matched_occurrences,
  round(100.0 * count(*) / sum(count(*)) OVER (), 4) AS share_of_matched_occurrences,
  round(100.0 - 100.0 * max(count(*)) OVER () / sum(count(*)) OVER (), 4) AS exact_top_spelling_undercount_pct
FROM matched GROUP BY type_code ORDER BY occurrences DESC, type_code;
