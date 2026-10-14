# OpenCode configs used by the runners

The runner copies one of these into each run's sandbox as `opencode.json` (a project config overrides the user's global one). Edit them here, so every change is in git.

| File | Used by | What it allows |
|---|---|---|
| `opencode.analysis.json` | A, C, B-revise | The model may write files and run `python3` / `ls` / `cat` / `head` / `mkdir` inside its folder. No web, no access outside the folder. At most **15 steps per run**. |
| `opencode.review.json` | B-critique | Review only: no file edits, no code execution. The shell tool stays in the request with a single harmless command (`true`) because the free tier rejects requests without it (HTTP 403, see E006). |

**15 steps per run** (E006): clear questions used ≤ 11; ambiguous questions hit a 10-step cap 8/12 times, and 15 rescued one more run at +33% time. It is a per-run budget, identical for every run. B makes three runs per item, so it spends more steps than A or C in total; that extra spend is B's cost and is reported next to its effect.
