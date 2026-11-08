"""C3 (just-in-time data notes): facts the notes are built from, computed by code from the file the agent reads.
Same rule as the profile (G1): numbers and column facts only, every column by the same rule, no outcome aggregates.
Run: ~/.poppy/venv/bin/python experiments/E010-loop/jit/make_facts.py  -> facts.json
"""
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[3]
PARQUET = ROOT / "data" / "processed" / "nyc_crashes.parquet"
c = duckdb.connect()
c.execute(f"create view t as select * from read_parquet('{PARQUET}')")
cols = [r[0] for r in c.execute("describe t").fetchall()]
d0, d1 = c.execute("select min(crash_date), max(crash_date) from t").fetchone()
facts = {"date_min": str(d0), "date_max": str(d1), "columns": {}}
for col in cols:
    overall = c.execute(f'select 100.0 * count(*) filter (where "{col}" is null) / count(*) from t').fetchone()[0]
    per_year = dict(c.execute(f'select year(crash_date), 100.0 * count(*) filter (where "{col}" is null) / count(*) '
                              'from t group by 1').fetchall())
    if overall == 0 and not any(per_year.values()):
        continue
    facts["columns"][col] = {"overall": round(overall, 1), "per_year": {str(y): round(v, 1) for y, v in sorted(per_year.items())}}
(Path(__file__).parent / "facts.json").write_text(json.dumps(facts, indent=1))
print(len(facts["columns"]), "columns with NULLs")
