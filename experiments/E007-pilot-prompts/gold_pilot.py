"""Gold numbers for the pilot questions (independent SQL). Ambiguous/insufficient items get the reference
series a careful analyst would use; the answer key for them is qualitative (see rubric in PROTOCOL.md)."""
import json, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = HERE.parents[1] / "data" / "processed" / "nyc_crashes.parquet"
W = "year(crash_date) BETWEEN 2013 AND 2025"
SQL = {
 "K1": f"SELECT year(crash_date) k, sum(number_of_pedestrians_killed) v FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1",
 "K2": f"SELECT dayofweek(crash_date) k, count(*) v FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1",
 "K3": f"SELECT year(crash_date) k, sum(number_of_motorist_killed) mot, sum(number_of_cyclist_killed) cyc FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1",
 "A1": f"SELECT year(crash_date) k, sum(number_of_pedestrians_injured) inj, sum(number_of_pedestrians_killed) killed FROM '{P}' WHERE {W} AND upper(borough)='BROOKLYN' GROUP BY 1 ORDER BY 1",
 "A2": f"SELECT CASE WHEN hour(crash_time) BETWEEN 6 AND 17 THEN 'day' ELSE 'night' END k, count(*) crashes, sum(number_of_persons_killed) killed, sum(number_of_persons_injured) injured FROM '{P}' WHERE {W} GROUP BY 1",
 "I1": f"SELECT year(crash_date) k, sum(number_of_motorist_killed) v FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1",
}
con = duckdb.connect()
gold = {q: [[x if isinstance(x, str) else float(x) for x in r] for r in con.execute(s).fetchall()] for q, s in SQL.items()}
(HERE / "gold_pilot.json").write_text(json.dumps(gold, indent=1))
for q, rows in gold.items(): print(q, len(rows), rows[:2])
