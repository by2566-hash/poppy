# E006 — Can mimo-v2.6-flash-free be the single phase-1 model?

**Result: yes, as a bounded OpenCode agent run.** In 18 runs of step ① (6 clear questions × 3 repeats) mimo finished every run, produced chart + plotted values + written answer every time, matched the gold numbers on all 18 (16 fully, 2 at 90%), and read 5/5 charts correctly. **But step ① cannot be a strict single tool-less call on the OpenCode free tier**, so the phase-1 design needs one wording change (section 4).

Stability here means what the team defined: call success, structured-output compliance, consistency across repeats. Answer quality is what the experiment measures, so it is not a selection criterion.

## 1. Step ① as a bounded agent run (final screen)

Config: `agent.build.steps = 10`; bash limited to python/ls/mkdir/head/cat; `external_directory`, `webfetch` denied; each run in its own sandbox and `XDG_DATA_HOME`; 420 s timeout; stdin closed. Prompt: question + data dictionary + "write and run code yourself; save `./out/initial.png`, `./out/values.csv`; end with `ANSWER:`". Script: `run_screen_agent.py`; raw: `screen_agent_runs.json`.

| Criterion | Result |
|---|---|
| Call success (no error, no timeout) | **18 / 18** (0 timeouts, 0 API errors) |
| Output compliance (chart + values file + `ANSWER:` ≥ 15 chars) | **18 / 18** |
| Core numbers equal gold SQL | 16 / 18 at 100%; 2 at 90% (both P5, see below) |
| Time per run | median 65 s, max 134 s |
| Tool calls per run | median 6, max 11; 2 / 18 reached the 10-step cap and still finished |
| Input tokens per run | median ≈ 6.5k |

Consistency across the 3 repeats: the year/category totals agree in every repeat; only 6 / 18 values files are byte-identical, because runs add or drop helper columns (`crashes`, `pct`). **P5** is a real interpretive split: 2 of 3 repeats listed the top 10 *specific* factors and dropped "Unspecified" (the gold list keeps it as the largest). Whether "Unspecified" counts is exactly the kind of choice the evaluation should record.

## 2. Reading charts (needed by B's critique step)

5 charts generated from gold data, 3 questions each (tallest point, a value at a given x, top y-axis tick), default agent config, `-f chart.png`.

| | Result |
|---|---|
| Highest point / bar | 5 / 5 (one tie, 2013 = 2021 = 297 deaths; the model gave 2021, correct) |
| Value within 10% | 5 / 5 (errors 0 – 0.5%) |
| Top y tick | 5 / 5 |

n = 5 charts of simple shapes. Enough to show mimo can read values off a chart; not an estimate of accuracy on cluttered charts. For comparison (E005): big-pickle and nemotron answered "no image" on the same kind of task.

## 3. What did not work (and cost a day)

| Attempt | Outcome | Cause |
|---|---|---|
| Forbid tools (`bash: deny`, or `tools.bash/read: false`) | HTTP 403 "free tier can only be used from within OpenCode" | The free-tier gateway requires **both `bash` and `read`** in the request; other tools can be removed |
| `agent.build.steps = 1` (forces one text-only step) | 18 / 18 calls succeeded, 0 tool calls, **but 18 / 18 replies contain a "Maximum steps reached… recommended next step" message and no real answer** | The step-limit prompt is injected from step 1; the model narrates what it would do. Screen discarded (`*_INVALID.*`) |
| Default config + "reply in this format" | 13 tool calls, searched the filesystem outside the sandbox, read other runs' logs | An agent model does not obey "single call" from the prompt alone |
| First screening batch in background mode | all 18 calls stalled to the 300 s timeout | `opencode run` reads stdin; a background process with an open stdin never sends EOF. Fix: `stdin=DEVNULL` |

## 4. Consequence for the phase-1 design

1. **"One model call" cannot be enforced on the OpenCode free tier.** Options: (a) **step ① = one bounded agent run in which the model writes and executes its own code** (this screen; what OpenCode is designed for; no API keys; matches E004); (b) call a free chat-completions endpoint directly (OpenRouter, NVIDIA, Groq are on Ryan's list) for true single calls; needs keys and leaves OpenCode out of the loop.
2. **Recommendation: (a).** Count "runs" instead of "calls": A = 1 run, B = 3 runs, C = 1 run (each ≤ 10 steps). Keep the team's artifacts: chart, plotted values, run log, and the code the model wrote (re-executable by the harness for reproducibility).
3. **The written answer is only grounded when the model has seen the numbers.** In a strict "generate code + answer, then execute" design the answer is written before execution, so any number in it is a guess. In (a) the model computes first. In B, the revise run must also be allowed to execute, or the harness must re-write the answer from the revised values.
4. **Model: mimo.** It is the only free model that reads images (needed by B's ③), and it passed all three stability criteria on the clear questions.

## 5. Limits

- 18 runs, clear questions only. In E004 mimo timed out on 4 / 8 *vague* questions (900 s cap); the ambiguous and insufficient-evidence questions need their own screen before the formal run.
- Zen free models are "free for a limited time", and some train on submitted data: public data only; finish the formal runs soon.
- Prompts were not tuned; the pilot round (phase-1 doc section 8) comes next.
