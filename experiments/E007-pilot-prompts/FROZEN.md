# Frozen prompts and configs (2026-10-16)

Frozen after pilot iteration 3 (protocol limit: 3 iterations). No edits from here on; a change needs a new protocol version and a re-run of every arm that uses it. Every formal run records these hashes in `meta.json` (`env.prompt_sha`, `env.config_sha`, 16-character prefixes).

| Prompt | SHA-256 |
|---|---|
| `A.v1.md` | `5ea316c0265121d0278a9ef4c09d182c13c010a1d4afb19b35973cd81756c935` |
| `B_critique.v4.md` | `f8bfefe032067c9d89463f90a7349c9b0afb29521daedae4e06c2592de17d038` |
| `C_selfcheck.v3.md` | `96250d0fc29b340f4b69992275499071ca39f4aae89472be29bec10664824cf9` |
| `B_revise.v3.md` | `38af1935bf2f386e79331ab7880d4391aebad6d95257bdbac07aa31e5da4f919` |

| Config | SHA-256 |
|---|---|
| `config/opencode.analysis.json` | `51a2bdaf303e06c45af1bba6a8dca5eb749a633c5ddcec211b0b8c2f888aef75` |
| `config/opencode.review.json` | `beba3f25da37e6afffc3817718a20a99124725c85dc96f9bd591179d44792814` |

- A: `A.v1.md` (frozen since 2026-10-14, never edited).
- B: review `B_critique.v4.md`, revise `B_revise.v3.md`, run as `run_pilot.py B v4 v3 <A_label>`.
- C: `C_selfcheck.v3.md`, fixed 2026-10-19 after one format check on mimo (see ITERATIONS.md); not tuned. SHA-256 `96250d0fc29b340f4b69992275499071ca39f4aae89472be29bec10664824cf9`.
- Harness at freeze: sandbox v2, review in its own folder, review timeout 420 s, other runs 600 s, 15 steps per run, zero-output timeout retried once, B end states `B_STATES`.

Iteration 3 total model time on 5 runnable items: 13.8 min.

## Phase 2 prompts (arm D)

| Prompt | SHA-256 | Frozen |
|---|---|---|
| `D_enumerate.v1.md` | `a18643123c55bfd00cabea8dcbb4f806463a50d79723d3e5e42ef355e3b14e19` | 2026-10-20 (k = 3, cap 25; baseline for every D comparison) |
| `D_enumerate.v2.md` | `bde1fd02f5b3e576618cf5f2429d6e9d31904328a8c3dfce675a3c753b598d0a` | 2026-11-04 (free k, `interpretation` = which part of the asked question the option answers and why; confirmed by Bo from `D_enumerate.v2.draft.md`; run as `PILOT_K=0 run_pilot.py D v2`) |

## Harness for arm D from E009-F3 on (frozen 2026-11-06, Bo)

| File | SHA-256 |
|---|---|
| `experiments/E007-pilot-prompts/run_pilot.py` | `edd5532fd8eb4ef34965a4128edab4113b06da3e94a6ce2d84669c0a8cbc7479` |
| `experiments/E006-mimo-screen/run_screen.py` | `7616f48b5d3be9db98bbabe9142afc69fbabd36da602658f74c65d3c1845d118` |

Change from the F1/F2 harness: `run_enumerate` passes `done=enumerate_done` to `call_model`. When `out/options.json` parses and the final step wrote `ANSWER:` without a tool call, the harness ends an OpenCode process that does not exit: 10 s after a `step_finish` with reason `stop`, or 120 s after the stream ends on the ANSWER text. Such a run is `answered_no_exit = true`, `timed_out = false`, and counts as `call_ok`. Every other arm calls `call_model` without `done` and is unchanged. Checked on all 73 stored D runs: the 67 normal completions give `stop`; the 3 F2 runs that answered and then hung give `stop` / `text`; the 2 timeouts without a final answer and the stopped attempt give none. A fake-OpenCode test covers the kill path (stop 6 s, text 10 s with a test grace of 8 s, no answer: timeout). Teammates check these hashes before an F3 run.
