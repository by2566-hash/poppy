"""Diagnostic H6 (2026-11-08): D v2 baseline with OpenCode's external skill scan switched off, i.e. F1's context.

Found: OpenCode auto-loads ~/.claude/skills/*/SKILL.md into the agent's skill list; architecture-scout appeared there on
2026-11-07 03:23, so every run since carries its description (first-step prompt 5,401 tokens on F1, 5,638 today).
This wrapper does not edit the frozen harness: it sets the two OpenCode switches in this process's environment
(call_model passes os.environ through) and calls run_pilot.run_enumerate with its own label, as the F2 wrapper did.
Run: POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E010-loop PILOT_K=0 PILOT_STEPS=35 ~/.poppy/venv/bin/python <this file>
"""
import json, os, sys
from pathlib import Path

os.environ["OPENCODE_DISABLE_EXTERNAL_SKILLS"] = "1"
os.environ["OPENCODE_DISABLE_CLAUDE_CODE"] = "1"
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "E007-pilot-prompts"))
import run_pilot as rp  # noqa: E402

assert not rp.PROFILE_TEXT and not rp.JIT_DIR, "plain D v2 only"
LABEL = "D-v2-kfree-hermetic" + rp.SUFFIX
pf = rp.HERE / "prompts" / "D_enumerate.v2.md"
res = []
for q in rp.QS:
    for r in (1, 2, 3):
        m = rp.run_enumerate((LABEL, q, r, pf, 0))
        sb = rp.SANDBOX / LABEL / f"{q}-r{r}"
        ev = [json.loads(l) for l in (sb / "events.jsonl").read_text().splitlines() if l.strip()]
        t = next(e for e in ev if e["type"] == "step_finish")["part"]["tokens"]
        m["first_step_prompt_tokens"] = t["input"] + t["cache"]["write"] + t["cache"]["read"]
        m["opencode_env"] = {k: os.environ[k] for k in ("OPENCODE_DISABLE_EXTERNAL_SKILLS", "OPENCODE_DISABLE_CLAUDE_CODE")}
        (sb / "meta.json").write_text(json.dumps(m, indent=1))
        print(f"  first-step prompt tokens {m['first_step_prompt_tokens']}", flush=True)
        res.append(m)
out = rp.RESULTS.parent / "runs"; out.mkdir(exist_ok=True)
(out / f"{LABEL}.json").write_text(json.dumps(res, indent=1))
print("saved", LABEL)
