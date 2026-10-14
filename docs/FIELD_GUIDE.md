# Learnings Field Guide

Format (99P Labs capstone instructions): date — a general lesson, then why it holds, based on our experiments. Written for a future builder.

---

**2026-10-03 — Isolate a coding agent's configuration before using it as an evaluation subject.**
Coding agents silently load user-level instructions, MCP servers and plugins. Our Codex default profile carried a global instruction to "separate facts from assumptions" and "consider data quality" — exactly the behaviors we score — and disabling project docs did not remove it (E000). Use a dedicated profile with its own login and a minimal config, and never share the main credential file between profiles.

**2026-10-03 — Agent-written data cards look complete; verify them with an independent pass.**
Codex produced a clean, well-sourced data card in 12 minutes (E001), and the core numbers matched our independent queries exactly. But it framed one trap misleadingly ("one e-bike spelling misses 59%" mixed e-bikes with scooters and mopeds; the real figure is 3%) and missed two traps that matter more: a broken data tail and injured e-riders hidden outside every mode column (E001-review, R001). Correct numbers with the wrong denominator are the failure mode this project targets.

**2026-10-03 — In NYC open data, total crash counts are not a safety series.**
After the NYPD stopped recording most property-damage-only crashes (pilot 2019, citywide April 2020), property-damage-only crashes fell 71% from 2019 to 2025 while injury crashes fell 18% and deaths did not fall the same way. Any vague "is it getting safer?" question needs outcome-based measures and an exposure denominator, not crash counts.

**2026-10-04 — For vague questions, free models differ more in *when* they decide than in *whether* they can.**
Across 24 runs (E004), the best free model made acceptable ask / enumerate / proceed decisions on every question it finished, but often only after 20+ tool calls; another explored until timeout and never asked. Measure time and tool calls until the decision, not just the final answer, and run each cell several times: one model reversed its conclusion on the same question between runs.

**2026-10-04 — Denying web access does not stop agents from using outside numbers.**
With web fetch disabled, models still computed per-capita and per-trip rates from population and city statistics recalled from memory, without saying so. Treat any number not derivable from the provided data as a finding to flag, and score it.

**2026-10-14 — "One model call" is a harness property, not a prompt property.**
A free-tier agent model told to answer in a fixed format still made 13 tool calls, explored the filesystem outside its sandbox and read other experiments' logs. Enforce single-call behaviour in the harness (a step limit), not in the prompt, and record tool-call counts as a data-quality field. Also check the access path: the free-tier gateway returned 403 whenever the shell or read tool was removed, which silently invalidated a whole batch until we looked at the error text.

**2026-10-14 — Background `opencode run` hangs unless stdin is closed.**
`opencode run` appends piped stdin to the message and waits for EOF. A batch started in the background inherited an open pipe and all 18 calls stalled to the timeout with zero output. Always pass `stdin=DEVNULL`; a harness that reports "timeout" without checking this will blame the model.

**2026-10-14 — A forced-stop prompt contaminates the output you are trying to measure.**
Limiting an agent to one step made every reply a narration of what it would do ("maximum steps reached; recommended next step…"), and a lenient parser scored some of them as compliant. Read raw outputs before trusting a screening metric, and flag known artifact phrases in the harness.

**2026-10-14 — In a "generate code and answer, then execute" design, the written answer is a guess.**
The answer is produced before any number exists. Either let the model execute and read its own results, or write the answer after execution from the plotted values.

**2026-10-14 — On a free tier, a "hang" is usually rate limiting; make the harness say so.**
OpenCode retries a rate-limited call three times and then waits, with an empty event stream. Our batch spent 600 s per item and logged six "timeouts" that were not model behaviour; two earlier batches had also been polluted. Run with `--print-logs --log-level ERROR`, match "Rate limit exceeded", stop at once and back off. Budget free-tier throughput before designing the number of runs (here: 3 arms × 10 questions × 3 repeats plus review calls ≈ 120+ runs).
