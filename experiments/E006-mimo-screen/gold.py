"""Gold numbers for the six screening questions, from independent SQL (DuckDB)."""
import json
import duckdb
from common import PARQUET, HERE

W = "year(crash_date) BETWEEN 2013 AND 2025"
SQL = {
    "P1": f"SELECT year(crash_date) k, sum(number_of_persons_killed) v FROM '{PARQUET}' WHERE {W} GROUP BY 1 ORDER BY 1",
    "P2": f"SELECT year(crash_date) k, sum(number_of_cyclist_injured) v FROM '{PARQUET}' WHERE {W} GROUP BY 1 ORDER BY 1",
    "P3": f"SELECT coalesce(nullif(trim(borough),''),'UNKNOWN') k, sum(number_of_pedestrians_injured) v FROM '{PARQUET}' WHERE {W} GROUP BY 1 ORDER BY 2 DESC",
    "P4": f"SELECT hour(crash_time) k, count(*) v FROM '{PARQUET}' WHERE {W} GROUP BY 1 ORDER BY 1",
    "P5": f"SELECT contributing_factor_vehicle_1 k, count(*) v FROM '{PARQUET}' WHERE {W} AND contributing_factor_vehicle_1 IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 10",
    "P6": f"SELECT year(crash_date) k, sum(number_of_cyclist_injured) cyc, sum(number_of_pedestrians_injured) ped FROM '{PARQUET}' WHERE {W} GROUP BY 1 ORDER BY 1",
}
con = duckdb.connect()
gold = {q: [list(map(lambda x: x if isinstance(x, str) else float(x), r)) for r in con.execute(s).fetchall()] for q, s in SQL.items()}
(HERE / "gold.json").write_text(json.dumps(gold, indent=1))
for q, rows in gold.items():
    print(q, len(rows), rows[:3])
