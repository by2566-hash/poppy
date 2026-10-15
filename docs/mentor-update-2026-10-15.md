# Phase 1 update for Ryan — 2026-10-15

**Change in framing.** Step ① is no longer "one model call, then Python runs the code". OpenCode's free tier cannot do a tool-less single call (removing tools returns HTTP 403; one forced step makes the model narrate instead of answer). So ① is one bounded agent run: the model writes and runs its own code, sees its numbers, then answers (≤ 15 steps, 600 s). That is also what an analyst gets today from Codex, Claude Code or OpenCode.

**The question becomes:** when an analyst uses an AI agent on a data file, is it worth adding an independent review step (B: a fresh-context reviewer that sees the chart but cannot run code, then a revision), or is telling the agent to check its own work enough (C)? A is the agent alone.

**Why B still has something to find.** In the pilot the agent fixed every error that crashed its code (6 in 10 runs), but not errors that run silently: a sum that dropped rows with NULLs, a ranking sentence contradicting the values. B's reviewer caught those.

**Pilot status.** The pilot checks that B runs as designed (inputs, outputs, boundaries), not how much it helps; that is the formal run's question. Along the way we found and closed sandbox gaps: the model could search the web and read files outside its folder. Every run now sees only its own folder and data file, with no network, enforced by OpenCode permissions plus a macOS sandbox, and tested.

Workflow figure with each step's inputs and outputs: `docs/figures/phase1-workflow.png`. Design: `docs/phase1-abc-design.md`.
