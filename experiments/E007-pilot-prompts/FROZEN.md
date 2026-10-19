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
