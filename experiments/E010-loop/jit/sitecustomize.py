"""C3 just-in-time data notes (E010 diagnostic candidate). Loaded by the agent's Python through PYTHONPATH=<sandbox>/.jit.

When the agent runs a DuckDB query on the crash file, this prints short factual notes to stderr about the columns that
query uses, next to the query's own output:
- a column the query filters on, groups by or aggregates has NULL values (share in the file, range by calendar year);
- the query has no date bound that leaves out 2012 or 2026, which the file covers only in part.
Rule as the profile (gate G1): numbers and column facts only, every column by the same rule, no advice, no outcome
aggregates. Each note is printed once per Python process. The note never changes the query or its result.
"""
import json
import re
import sys
from pathlib import Path

_FACTS = json.loads((Path(__file__).resolve().parent / "facts.json").read_text())
_SEEN = set()
_SEG_END = r"(?=\bgroup\s+by\b|\border\s+by\b|\blimit\b|\bhaving\b|\bunion\b|\bselect\b|\bqualify\b|\bwindow\b|$)"


def _range(col):
    f = _FACTS["columns"][col]
    py = {y: v for y, v in f["per_year"].items()}
    hi_y = max(py, key=py.get)
    return f"NULL in {f['overall']}% of rows in the file; by calendar year {min(py.values())}% to {py[hi_y]}% (highest {hi_y})"


def _segments(q, start):
    return [m.group(1) for m in re.finditer(start + r"(.*?)" + _SEG_END, q, re.S)]


def _notes(sql):
    q = sql.lower()
    if not re.search(r"crashes|parquet", q):
        return []
    out = []
    where = " ".join(_segments(q, r"\bwhere\b") + _segments(q, r"\bfilter\s*\(\s*where\b"))
    group = " ".join(_segments(q, r"\bgroup\s+by\b"))
    for col in _FACTS["columns"]:
        pat = r'(?<![\w.])"?' + re.escape(col) + r'"?(?!\w)'
        if re.search(pat, where):
            out.append(f"[data note] `{col}` is {_range(col)}. A condition on `{col}` is not true for rows where it is NULL.")
        if re.search(pat, group):
            out.append(f"[data note] `{col}` is {_range(col)}. Rows where it is NULL form a separate NULL group.")
        if re.search(r"\b(sum|avg|mean|count|min|max)\s*\(\s*(distinct\s+)?" + pat, q):
            out.append(f"[data note] `{col}` is {_range(col)}. SUM, AVG and COUNT of `{col}` skip rows where it is NULL.")
    upper = re.search(r"<\s*(date\s*)?'?2026|<=\s*(date\s*)?'?2025|between\s+\S+\s+and\s+(date\s*)?'?2025"
                      r"|<\s*make_date\(\s*2026|<=\s*make_date\(\s*2025", q)
    lower = re.search(r">=\s*(date\s*)?'?2013|>\s*(date\s*)?'?2012|between\s+(date\s*)?'?2013"
                      r"|>=\s*make_date\(\s*2013|>\s*make_date\(\s*2012", q)
    d0, d1 = _FACTS["date_min"], _FACTS["date_max"]
    if not upper:
        out.append(f"[data note] This query has no date bound before 2026; the file covers {d1[:4]} only from {d1[:4]}-01-01 to {d1}.")
    if not lower:
        out.append(f"[data note] This query has no date bound after 2012; the file covers {d0[:4]} only from {d0} to {d0[:4]}-12-31.")
    return out


def _emit(sql):
    try:
        for n in _notes(str(sql)):
            if n not in _SEEN:
                _SEEN.add(n)
                print(n, file=sys.stderr, flush=True)
    except Exception:  # noqa: BLE001  a note must never break the agent's query
        pass


def _install():
    try:
        import duckdb
    except Exception:  # noqa: BLE001
        return

    class _Conn:
        def __init__(self, con):
            object.__setattr__(self, "_con", con)

        def __getattr__(self, name):
            return getattr(self._con, name)

        def __enter__(self):
            self._con.__enter__()
            return self

        def __exit__(self, *a):
            return self._con.__exit__(*a)

        def execute(self, query, *a, **k):
            _emit(query)
            return self._con.execute(query, *a, **k)

        def sql(self, query, *a, **k):
            _emit(query)
            return self._con.sql(query, *a, **k)

        def query(self, query, *a, **k):
            _emit(query)
            return self._con.query(query, *a, **k)

    real_connect = duckdb.connect
    duckdb.connect = lambda *a, **k: _Conn(real_connect(*a, **k))
    for name in ("sql", "query", "execute"):
        real = getattr(duckdb, name, None)
        if real is not None:
            def wrap(query, *a, _real=real, **k):
                _emit(query)
                return _real(query, *a, **k)
            setattr(duckdb, name, wrap)


_install()
