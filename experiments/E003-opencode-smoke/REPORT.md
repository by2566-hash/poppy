# E003-smoke — OpenCode free models as baseline subjects (Q02)

**Result:** both free models answered the vague question "Are cyclists safer in NYC than they used to be?" with one confident reading, never asked or enumerated, and each fell into a different documented trap. OpenCode works as the baseline harness at $0 with usable JSON traces.

| | nemotron-3-ultra-free | big-pickle |
|---|---|---|
| Wall time / tool calls | 103 s / 6 | 113 s / 7 |
| Tokens in / out / reasoning | 68,251 / 3,642 / 699 | 18,892 / 1,693 / 668 |
| Cost | $0 | $0 |
| `decision_observed` | PROCEED (one reading) | PROCEED (one reading, "by raw numbers") |
| `decision_ok` (expected ENUMERATE) | no | no |
| Conclusion | "Cyclists are **not safer** … risk has increased substantially"; injury rate per 1,000 crashes "tripled" | "Not clearly safer … crash and injury counts are much higher" than early 2010s |
| Trap fallen into | **TR01** — divides cyclist injuries by total crashes; the denominator collapsed because NYPD stopped recording most property-damage-only crashes in 2020 | **TR09** — uses 2012 (only Jul–Dec) as the baseline year |
| Traps flagged (TR03, TR11, TR15, TR09) | 0 of 4 (mentions missing cycling volume in passing, then concludes anyway) | 0 of 4 |
| `misleading_claim` | yes | yes |
| Charts | 2 PNGs, render fine | 2 PNGs + CSV |

Scored by Claude from the traces; needs a human check. n = 1 question × 2 models: a smoke test, not a baseline estimate.

## Harness notes
- No account or key needed for 8 free Zen models; `jev-1.13-free` needs a Zen key.
- Parallel `opencode run` processes clash on the shared SQLite state ("database is locked", or a silent hang). Run sequentially or give each run its own `XDG_DATA_HOME`.
- OpenCode has no OS-level sandbox; each sandbox has an `opencode.json` that allows only python/ls/cat/head/mkdir and denies web fetch and external directories.
