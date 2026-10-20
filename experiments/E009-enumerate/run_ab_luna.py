#!/usr/bin/env python3
"""One A and one B pilot run on GPT-6 Luna, one pilot question per call (default K1), with the frozen prompts (A.v1, B_critique.v4, B_revise.v3).

  ~/venvs/poppy-luna/bin/python experiments/E009-enumerate/run_ab_luna.py A [qid]     # then
  ~/venvs/poppy-luna/bin/python experiments/E009-enumerate/run_ab_luna.py B [qid]     # qid: K1 (default) ... I1

The interpreter must live outside the repository: the model's python runs this interpreter under sandbox-exec,
which denies reads under the repository, so poppy/.venv cannot start there (first K1 attempt, 2026-10-19).
~/venvs/poppy-luna is the same Homebrew Python 3.13.13 with the same packages as poppy/.venv.

A thin launcher, not a new harness: it calls run_pilot.run_analysis / run_pilot.run_B (E007, unchanged) and
scripts/collect_runs.py (unchanged) with three settings passed from here:
  - labels A-v1-openai-gpt-6-luna and B-v1-openai-gpt-6-luna (requested names; run_pilot's own B label would be
    B-v4-v3-openai-gpt-6-luna). The prompt versions are recorded in meta.json env.prompt_sha by file name, as always.
  - collected runs go to experiments/E009-enumerate/results/<label>/<qid>-r1/ (the harness default, same as D);
    B reads A's collected run from there, as run_B reads A from the repo.
  - A's harness does not save the prompt (only D does); here the exact string passed to call_model is
    written to prompt.md for the A run. B keeps its own records (review_prompt.md, revise_prompt.md).
Sandbox: ../poppy-sandbox/E009/<label>/<qid>-r1/. Runs summaries: experiments/E009-enumerate/runs/<label>-<qid>.json.
"""
import json, os, sys
from pathlib import Path

os.environ["POPPY_EXP"] = "E009-enumerate"
os.environ["POPPY_MODEL"] = "openai/gpt-6-luna"
os.environ["POPPY_QSET"] = "pilot"

E009 = Path(__file__).resolve().parent
ROOT = E009.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E007-pilot-prompts"))
sys.path.insert(0, str(ROOT / "scripts"))
if Path(sys.prefix).resolve().is_relative_to(ROOT):
    sys.exit(f"interpreter {sys.executable} is inside the repository; the sandbox blocks it. Use ~/venvs/poppy-luna/bin/python")
import run_pilot as rp      # noqa: E402
import collect_runs as cr   # noqa: E402

Q, REP = (sys.argv[2] if len(sys.argv) > 2 else "K1"), 1
if Q not in rp.QS:
    sys.exit(f"unknown question id {Q}; pilot ids: {list(rp.QS)}")
A_LABEL, B_LABEL = "A-v1-openai-gpt-6-luna", "B-v1-openai-gpt-6-luna"
PROMPTS = rp.HERE / "prompts"
A_PROMPT, CRIT, REV = PROMPTS / "A.v1.md", PROMPTS / "B_critique.v4.md", PROMPTS / "B_revise.v3.md"
assert rp.RESULTS == cr.TARGET == E009 / "results"   # B reads A from results/<A_LABEL>/<qid>-r1


def collect(label):
    sys.argv = ["collect_runs.py", label, Q]
    cr.main()


def save_summary(label, res):
    (E009 / "runs" / f"{label}-{Q}.json").write_text(json.dumps(res, indent=1))


def run_A():
    if (rp.RESULTS / A_LABEL / f"{Q}-r{REP}").exists():
        sys.exit(f"{A_LABEL}/{Q}-r{REP} already exists; not overwriting")
    real = rp.call_model
    def capture(sb, prompt, **kw):      # record the exact prompt, then the unchanged call
        (Path(sb) / "prompt.md").write_text(prompt)
        return real(sb, prompt, **kw)
    rp.call_model = capture
    try:
        meta = rp.run_analysis((A_LABEL, Q, REP, A_PROMPT))
    finally:
        rp.call_model = real
    save_summary(A_LABEL, [meta])
    collect(A_LABEL)


def run_B():
    if (rp.RESULTS / B_LABEL / f"{Q}-r{REP}").exists():
        sys.exit(f"{B_LABEL}/{Q}-r{REP} already exists; not overwriting")
    meta = rp.run_B((B_LABEL, Q, REP, A_LABEL, CRIT, REV))
    # run_B copies A's run folder as its start; A's prompt.md (saved by this launcher) is not part of B's E007 file set.
    (rp.SANDBOX / B_LABEL / f"{Q}-r{REP}" / "prompt.md").unlink(missing_ok=True)
    save_summary(B_LABEL, [meta])
    collect(B_LABEL)


if __name__ == "__main__":
    {"A": run_A, "B": run_B}[sys.argv[1]]()
