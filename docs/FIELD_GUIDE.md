# Learnings Field Guide

Format (99P Labs capstone instructions): date — a general lesson, then why it holds, based on our experiments. Written for a future builder.

---

**2026-10-03 — Isolate a coding agent's configuration before using it as an evaluation subject.**
Coding agents silently load user-level instructions, MCP servers and plugins. Our Codex default profile carried a global instruction to "separate facts from assumptions" and "consider data quality" — exactly the behaviors we score — and disabling project docs did not remove it (E000). Use a dedicated profile with its own login and a minimal config, and never share the main credential file between profiles.

**2026-10-03 — Agent-written data cards look complete; verify them with an independent pass.**
Codex produced a clean, well-sourced data card in 12 minutes (E001), and the core numbers matched our independent queries exactly. But it framed one trap misleadingly ("one e-bike spelling misses 59%" mixed e-bikes with scooters and mopeds; the real figure is 3%) and missed two traps that matter more: a broken data tail and injured e-riders hidden outside every mode column (E001-review, R001). Correct numbers with the wrong denominator are the failure mode this project targets.

**2026-10-03 — In NYC open data, total crash counts are not a safety series.**
After the NYPD stopped recording most property-damage-only crashes (pilot 2019, citywide April 2020), property-damage-only crashes fell 71% from 2019 to 2025 while injury crashes fell 18% and deaths did not fall the same way. Any vague "is it getting safer?" question needs outcome-based measures and an exposure denominator, not crash counts.
