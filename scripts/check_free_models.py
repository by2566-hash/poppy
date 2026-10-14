#!/usr/bin/env python3
"""Check whether OpenCode's free models answer right now from THIS machine.

Usage:  python3 scripts/check_free_models.py [model ...]
Prints one line per model: OK / RATE_LIMITED / NO_RESPONSE / ERROR, with seconds.
Each check sends ~2 requests (one step + OpenCode's session-title call).

Why this exists: when the free tier rate-limits a model, `opencode run` retries silently and
its JSON event stream stays empty, so a batch looks "hung". The error is only visible in the
logs, which this script reads.
"""
import json, os, subprocess, sys, tempfile, time

MODELS = sys.argv[1:] or ["mimo-v2.6-flash-free", "nemotron-3-ultra-free", "big-pickle"]

def check(model, timeout=60):
    d = tempfile.mkdtemp(prefix="oc-check-")
    t0 = time.time()
    p = subprocess.Popen(
        ["opencode", "run", "--pure", "--print-logs", "--log-level", "ERROR", "--format", "json",
         "-m", f"opencode/{model}", "--dir", d, "--", "Reply with exactly OK."],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, stdin=subprocess.DEVNULL,
        env=dict(os.environ, XDG_DATA_HOME=os.path.join(d, ".oc")), cwd=d)
    err = ""
    while p.poll() is None and time.time() - t0 < timeout:
        time.sleep(1)
    if p.poll() is None:
        p.kill()
    out, err = p.communicate()
    secs = round(time.time() - t0, 1)
    if "Rate limit exceeded" in err:
        return "RATE_LIMITED", secs
    text = ""
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "text":
            text += e.get("part", {}).get("text", "")
        if e.get("type") == "error":
            return "ERROR: " + str(e.get("error", {}).get("data", {}).get("message", ""))[:80], secs
    if "OK" in text:
        return "OK", secs
    return "NO_RESPONSE", secs

if __name__ == "__main__":
    for m in MODELS:
        status, secs = check(m)
        print(f"{m:28s} {status:14s} {secs:6.1f}s", flush=True)
