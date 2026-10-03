SELECT year, crashes, pdo_crashes, injury_crashes, outcome_unknown
FROM (
  SELECT year(crash_date) AS year, count(*) AS crashes,
    count(*) FILTER (WHERE number_of_persons_injured=0 AND number_of_persons_killed=0) AS pdo_crashes,
    count(*) FILTER (WHERE number_of_persons_injured>0 OR number_of_persons_killed>0) AS injury_crashes,
    count(*) FILTER (WHERE (number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL)
      AND coalesce(number_of_persons_injured,0)=0 AND coalesce(number_of_persons_killed,0)=0) AS outcome_unknown
  FROM read_parquet('data/processed/nyc_crashes.parquet')
  WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
  GROUP BY 1
) ORDER BY year;
