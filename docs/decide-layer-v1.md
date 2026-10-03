# Decision layer (`decide()`) — v1 plan

- **Date:** 2026-10-03. **Status:** plan; nothing installed or purchased yet.
- **Use:** (1) routing a vague question to ASK / ENUMERATE / PROCEED; (2) L3 judging ("did the output flag trap TRxx?", "does this chart cover interpretation Ix?").

## 1. Contract

Adopt the shared "System One" request format as the `decide()` contract: a `state` plus named typed questions (`noul` = probability of yes, `choice` = distribution over options, `score` = distribution over ordered levels). Jev, OpenRouter, OpenCode Zen, CLM's `clm-serve`, Kev and Clef all accept `POST /v1/systemone` in this shape, so switching backends is a base-URL change. An LLM-logprob backend only needs a small adapter.

Rules that follow from documented weaknesses (Jev's own "jagged edges" page and independent studies):
- Compute every number, date comparison and trap fact in code; pass them as named fields in `state` (e.g., `pdo_change_2019_2020: -52%`). Never ask the model to do arithmetic on a raw table.
- Keep `state` ≤ 1.5k tokens (CLM truncates at 2,048).
- Run every item in two option orders, plus once with neutral option names (renaming options moved one study's AUC from .81 to .58).
- Do not use Jev's `confidence` field as a probability; it is a margin statistic.

## 2. Backends

| Backend | Open? | Runs where | Cost | Setup | Notes |
|---|---|---|---|---|---|
| **LLM logprobs** — Qwen3-8B / Qwen3.5-9B via Ollama native `/api/chat` (`think:false`, `logprobs`, `top_logprobs:20`, 1 token) | Yes | Local Mac (24 GB is enough) | $0 | Install Ollama + pull a ~5 GB model; ~0.5 day | Strongest open baseline; one study found Jev no better than plain label logprobs |
| **Jev** (TypeSafe, closed) | No | OpenRouter `typesafe/jev-1.13` (no waitlist) or OpenCode Zen `jev-1.13-free` (free for a limited time) | ~$0.02 for an 80-item pilot, or $0 on Zen | API key (user signs up); ~1 hour with `typesafe-sdk` | $0.042/M input tokens. Mid-tier accuracy in independent studies; needs recalibration on our labels |
| **Clef-flash** (Cloudflare, Apache-2.0, 9B) | Yes | Local via 4-bit MLX build (~7–8.6 GB peak) | $0 | ~0.5 day | Optional open decision model with the same API |
| CLM-8B (Apache-2.0) | Yes | Officially CUDA + vLLM; Mac only via community ports | $0 | Timebox to 1 day or drop | Weak on community decision benchmark (30 vs Jev 80); 2,048-token input |

Decision: run LLM logprobs + Jev first (cheapest credible pair), add Clef-flash if time allows, drop CLM-8B unless NYU HPC access appears.

## 3. Pilot (go / no-go screen, not a leaderboard)

- **Items (~80):** 40 routing items (3-way choice) + 20 trap-flag items (yes/no) + 20 coverage items (yes/no per interpretation). Two people label independently; their kappa is the ceiling.
- **Metrics:** accuracy, macro-F1, Cohen's kappa vs settled labels; Brier score, log loss (clip at 0.001), top-label ECE with 5 equal-mass bins, reliability diagram; AUROC of confidence for spotting errors; accuracy-vs-coverage curve (sets the ASK threshold); temperature scaling with 5-fold cross-fitting; flip rate under option reordering / renaming; McNemar and paired bootstrap for comparisons.
- **Power caveat:** at n ≈ 80, accuracy is known to about ±10 points and kappa to about ±0.15–0.2; ECE differences under ~0.05 are noise.
- **Effort:** ~12–15 person-hours of labeling and spec, ~2 days of backend setup, ~2 days of analysis.

## 4. OpenCode fit

- `opencode run --format json` emits JSON events (step_start / step_finish with cost and tokens, tool_use with timing, text, reasoning, error) — usable as traces; pass `--auto` or permission prompts are auto-rejected.
- `decide()` can be exposed to OpenCode as a custom tool (`.opencode/tools/*.ts`) or an MCP server; custom agents live in `.opencode/agents/*.md`.
- Free Zen models (all "for a limited time") include `jev-1.13-free`; a Zen key needs sign-up and billing details. Some free models train on submitted data — public data only.
