#!/usr/bin/env python3
"""Verify that this machine matches the team's experiment environment before any run.

Usage:  python3 scripts/check_env.py
Exit code 0 = OK to run experiments; 1 = fix the FAIL lines first.

Checks: OpenCode version, Python version, pinned Python packages (requirements.txt),
and the content fingerprint of data/processed/nyc_crashes.parquet (row count, sums, date range).
The raw CSV checksum is only a warning: re-exports can differ byte-wise with identical content.
"""
import hashlib, json, platform, subprocess, sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = json.loads((ROOT / "scripts" / "env_expected.json").read_text())
fails, warns = [], []

def ok(msg): print(f"  OK    {msg}")
def fail(msg): fails.append(msg); print(f"  FAIL  {msg}")
def warn(msg): warns.append(msg); print(f"  WARN  {msg}")

print("OpenCode")
try:
    v = subprocess.run(["opencode", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    (ok if v == EXP["opencode_version"] else fail)(f"opencode {v or '?'} (expected {EXP['opencode_version']})")
except FileNotFoundError:
    fail("opencode not found on PATH (install it: https://opencode.ai)")

print("Sandbox")
# Same profile as run_screen.NO_NET: the model's python must not reach the network.
NO_NET = "(version 1)(allow default)(deny network-outbound (remote ip))"
try:
    probe = subprocess.run(["/usr/bin/sandbox-exec", "-p", NO_NET, sys.executable, "-c",
                            "import socket; socket.create_connection(('1.1.1.1', 53), 3)"],
                           capture_output=True, text=True, timeout=20)
    blocked = probe.returncode != 0 and "not permitted" in probe.stderr
    (ok if blocked else fail)("sandbox-exec blocks the model's python from the network"
                              + ("" if blocked else f" (probe: {probe.stderr.strip()[-120:] or 'connected'})"))
except FileNotFoundError:
    fail("/usr/bin/sandbox-exec not found (macOS only)")

print("Python")
py = platform.python_version()
(ok if tuple(map(int, py.split(".")[:2])) >= tuple(map(int, EXP["python_min"].split("."))) else fail)(
    f"python {py} (need >= {EXP['python_min']})")
for line in (ROOT / "requirements.txt").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, want = line.split("==")
    try:
        have = metadata.version(name)
        (ok if have == want else warn)(f"{name} {have} (pinned {want})")
    except metadata.PackageNotFoundError:
        fail(f"{name} missing (pip install -r requirements.txt)")

print("Data")
parquet = ROOT / "data" / "processed" / "nyc_crashes.parquet"
if not parquet.exists():
    fail("data/processed/nyc_crashes.parquet missing (see docs/status: build the data)")
else:
    try:
        import duckdb
        r = duckdb.connect().execute(
            f"SELECT count(*), sum(collision_id), min(crash_date)::VARCHAR, max(crash_date)::VARCHAR, "
            f"sum(number_of_persons_killed), sum(number_of_persons_injured) FROM '{parquet}'").fetchone()
        got = {"rows": r[0], "sum_collision_id": int(r[1]), "min_date": r[2], "max_date": r[3],
               "sum_killed": int(r[4]), "sum_injured": int(r[5])}
        diff = {k: (got[k], v) for k, v in EXP["data_fingerprint"].items() if got[k] != v}
        (ok if not diff else fail)("parquet content fingerprint" + ("" if not diff else f" differs: {diff}"))
    except Exception as e:  # noqa: BLE001
        fail(f"could not read parquet: {e}")
raw = ROOT / "data" / "raw" / "nyc_crashes_h9gi-nx95.csv"
if raw.exists():
    h = hashlib.sha256()
    with open(raw, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    (ok if h.hexdigest() == EXP["raw_csv_sha256"] else warn)("raw CSV sha256" + (
        "" if h.hexdigest() == EXP["raw_csv_sha256"] else " differs (fine if the parquet fingerprint is OK)"))

print()
if fails:
    print(f"NOT READY: {len(fails)} failure(s). Fix them before running experiments.")
    sys.exit(1)
print("READY" + (f" ({len(warns)} warning(s))" if warns else ""))
