# Mentor brief — Ryan, week of 2026-10-09

Plan: 8 minutes of talking, the rest is discussion. Screen-share pointers are in **[screen: …]**.

---

## 1. The talk

### Opening (30 s) — [screen: README.md]

"Last week we had a direction. This week we have evidence. Three things happened:
we picked a scenario and checked the data, we built a catalog of data traps that
becomes our eval ground truth, and we ran 24 baseline runs on OpenCode's free models.

The headline: free models are NOT bad at vague questions. They are inconsistent,
slow, and expensive at them. That changes what Poppy needs to be."

Point at README first paragraph: "This is the one-liner. Poppy takes a vague
question, decides whether to ask, list interpretations, or just proceed, and flags
traps in the data."

### Block 1 — Scenario and data (90 s) — [screen: docs/scenario-data-v1.md, section 3 trap table]

"Scenario: NYC traffic safety. 2.27 million police-reported crashes, 2012 to mid-2026.
The user we imagine is a journalist or fact-checker who has to decide whether a claim
like 'Vision Zero is failing' holds up. We picked it because the vague questions are
real — they are in DOT press releases and City Council hearings — and because the data
has 17 documented traps."

Point at TR01:
"In April 2020 NYPD stopped recording most crashes with no injuries. Total crashes fell
about 60 percent. Injury crashes fell 18. Deaths did not fall. Any agent that plots
'crashes over time' and says 'things got safer' is wrong, and it looks convincing."

Point at TR03:
"Since 2021, injured e-bike riders are counted in total injuries but in none of the
pedestrian, cyclist, or motorist columns. About 2,000 people a year are invisible if
you look at the cyclist column only."

Effort: "The data side is light on purpose. The crash table rebuilds in 7 seconds.
We checked Ohio — no scriptable public download. For Ohio and Honda questions we would
use FARS, the national fatal-crash file, which has a state code and vehicle make."

### Block 2 — Baseline (2 min) — [screen: experiments/E004-opencode-baseline/REPORT.md]

"We wrote 8 vague questions — from a control like 'how many people died each year' to
'is my street dangerous', which can only be answered by asking back. We ran them through
3 free OpenCode models with a plain prompt, no hints."

Outcomes table — three findings:

1. "The best model, big-pickle, made the right call on all 7 questions it finished.
   But it took 2 to 5 minutes and up to 27 tool calls each time. Another model explored
   for 15 minutes and timed out on both questions where the right answer was just to ask
   'which street?'"
2. "The same model, same question, gave opposite conclusions in two runs. A single-run
   eval means nothing. We need repeats."
3. "We disabled web access. Models still pulled population numbers and DOT statistics
   from memory to compute per-capita rates, and did not say so."

One-line demo — [screen: SCORES.md, row Q04]:
"Same question — 'did crashes go down after COVID?' One model says 'yes, dropped
dramatically.' Another says 'the drop is mostly a reporting change; deaths went up.'
Both charts look professional. Only one is right."

### Block 3 — What this changes (45 s) — [screen: docs/direction-v1.md, section 4]

"The gap is not 'can the model judge.' It is 'can it judge early, cheaply, and the same
way every time.' That points to a small, cheap decision step BEFORE any exploration:
ask, enumerate, or proceed. And to an eval that measures time-to-decision and
run-to-run agreement, not only the final answer."

### Block 4 — Honest limits (30 s) — [screen: experiments/LOG.md, E001-review and E004]

"Three caveats. Eight questions is a pilot, not a benchmark. The scoring was done by an
LLM against an answer key I wrote — that is circular, and we are fixing it this week
with all three of us scoring independently. And we learned this the hard way: Codex
built our data card, the numbers were all correct, and it still missed the two most
important traps. Agent output gets an independent check from now on."

### Close (15 s)

"What we want from you: push back on the scenario, and three questions at the end."

---

## 2. Current design (if asked "what does Poppy look like")

```
question
  │
  ▼
[0] decide()     → ASK / ENUMERATE / PROCEED      cheap, structured, swappable backend
  ▼
[1] plan         → each interpretation = {metric, dimension, filter, time window}
  ▼
[2] trap check   → code looks up which traps touch those columns and dates
  ▼
[3] execute      → DuckDB SQL + Vega-Lite spec (not free-form Python)
  ▼
[4] critique     → rule lint now, vision model later
  ▼
view = {decision, interpretations, charts, caveats, trace}
```

Two design questions to put on the table:

1. **Open-book or closed-book?** Does the agent read the trap catalog, or must it find
   traps itself? Closed-book tests exploration (research value). Open-book tests
   following (product value — what a semantic layer or "context" does in Hex and
   Databricks). We want both: "once you give the model the notes, does it still fall in?"
2. **Free Python or SQL + declarative charts?** One model spent 15 minutes debugging its
   own classifier until timeout. SQL + Vega-Lite is lintable, diffable, and stops runaway
   loops. We lean toward restricting in v0 — fewer rules.

---

## 3. Questions Ryan will likely ask

**"Give me the one-liner."**
"An agent that, given a vague question, decides whether to ask, list interpretations,
or proceed — before it touches the data — plus an eval harness that measures whether it
chose well. The harness is 80 percent of the work."

**"Why not just put 'state your assumptions and check for traps' in the prompt?"**
"That is literally our next experiment." [screen: experiments/E002-baseline/prompts/policy.md]
"Same models, same questions, this one added block. If prompting closes the gap, Poppy
becomes thin — the value is the trap catalog and the harness. If models still explore
for 15 minutes before deciding, a structured decision layer is justified. Either result
is a finding, and it costs zero to run."

**"How do you define 'good'?"**
"We stopped trying to define a good chart in the absolute. For vague questions we score
three concrete things with ground truth written before the run: Did it make an
acceptable decision? Which legitimate interpretations did it cover? Which documented
traps did it flag or fall into? Chart quality comes later as pairwise human preference —
relative, like you suggested."

**"Who wrote the answer key?"**
"I did, and that is the weakest link. Two fixes this week: all three of us score the
finished runs independently and report agreement. And the interpretation lists come
from real public arguments — Streetsblog, the Comptroller's report, Council hearings."

**"Why NYC? We are in Ohio."**
"We checked Ohio first. The state site needs a CAPTCHA and emails a link — not
scriptable. Columbus has a static 2018–2022 layer with no person data. For Ohio and
Honda questions we would use FARS in phase two. NYC gives us 17 verified traps and
questions our NYU raters will recognize. Chicago is our transfer test."

**"Where is the Honda connection?"**
"Direct: Honda's public goal is zero traffic deaths by 2050, half by 2030. The
vulnerable-road-user questions are the ones your safety researchers ask. Indirect:
ask-versus-proceed is the problem every data agent on an engineering team has. Your
research-to-code pipeline has the same shape — vague goal, many valid outputs."

**"Are you building on OpenCode?"**
"Yes. Baseline harness now, Poppy's runtime later. Free Zen models, no account, JSON
event traces. Two things we hit: parallel runs lock the shared database — fixed with
per-run data directories. And OpenCode has no OS-level sandbox, so we restrict each run
to Python plus a few read-only commands and deny web access."

**"What about Jev?"**
"We looked at it for the decision step. Pros: reachable through OpenRouter without the
waitlist, costs cents, returns typed probabilities. Cons: independent studies show
mid-tier accuracy and answers that flip when you rename the options, and TypeSafe's own
docs say it is weak at arithmetic and dates — our whole domain. So we compute trap facts
in code and only ask it to route. One experiment arm next to local Qwen logprobs and an
open model called Clef. Not a dependency — open source is the rule."

**"Biggest risk?"**
"Scope creep on the agent. Every model did impressive exploration, and it is tempting
to build a better explorer. Our rule: the agent stays thin, the eval gets deep. Second:
NYC data has been frozen since June. We pin the snapshot and never say 'live'."

**"What do you need from me?"**
1. "Can we get the 99P datasets on your site? Telematics or V2X would be a strong
   phase-two transfer test."
2. "Is a closed model okay inside an experiment if it costs cents and is not a dependency?"
3. "Is there anyone at HRI who asks these questions for real? A safety researcher's
   vague questions would beat ours."

---

## 4. Harder follow-ups

**"Your traps are just data-quality issues. What is new?"**
"The traps are not the new part. The measurement is. Nobody has a benchmark that scores
when an agent should ask versus proceed on vague visualization questions, on real data,
with the cost of unneeded questions included. VisInteract measures interaction but not
over-asking. The catalog is how we make ground truth cheap."

**"Three models, one run each, eight questions. That is not a baseline."**
"Agreed. We labeled it a pilot. Its job was to tell us what to measure, and it did —
time-to-decision, timeout rate, unsourced numbers, run-to-run agreement. The real
baseline is 3 repeats per cell, 30-plus questions, human-scored."

**"How will you know Poppy is better, not just different?"**
"Same questions, same models, three arms: plain prompt, policy prompt, decision layer.
Primary metric: decision accuracy and over-ask rate. Secondary: traps flagged, time to
decision, cost. Then pairwise human preference on the final view against the one-shot
output — our DS teammate owns that design."

**"Open-book sounds like cheating."**
"It is what every real analytics team does — they keep notes on their data. The
interesting question is whether models follow notes they are given. If they still fall
into TR01 with the note in front of them, that is a stronger finding than missing it blind."

**"What did you get wrong this week?"**
"Three things. Codex missed the two biggest traps while reporting correct numbers. We
ran OpenCode in parallel and hit a database lock. And two of our 'verified' data claims
were wrong — the person table starts in 2012 not 2016, and the data freeze is worse than
we said: death counts are null for 88 to 100 percent of May and June 2026. All in the log."

---

## 5. Next phase — propose and ask

**Propose** — [screen: experiments/LOG.md, E004 "Next" line]:
"Before next meeting, two things that cost nothing. First, the policy-prompt arm — same
24 runs with the decision instruction. That answers 'prompt or system'. Second, human
scoring: all three of us score the 18 finished runs and report agreement. That fixes the
circularity and gives our first human-labeled data.

With those we write Proposal v1 — one and a half pages: problem, baseline evidence, the
five-step design, eval metrics, milestones, and who owns what."

**Ask Ryan:**
1. "Does the journalist persona feel right, or should we aim at a safety researcher from day one?"
2. "Open-book and closed-book — both, or commit to one?"
3. "Restricting the agent to SQL plus declarative charts — good constraint or too tight?"

**If "why not just build the agent now?":**
"Because we do not yet know how thick it needs to be. One 50-minute experiment tells us.
Building first would be guessing."

**If "what will the demo look like?":**
"A question goes in. The output is a small page, not a chat bubble: the decision and why,
two to four charts each with one line of reasoning, a caveats box with the traps that
apply, and a link to the full trace. Visualization is not just chat."

---

## 6. Three things to remember

1. **Say "we".** One team voice. "X is leading the scoring protocol" is fine.
2. **Trends in words, not percentages.** "7 of 7" is visible in the output. "Misleading
   claim 3 of 7" is a judgment — add "by our preliminary scoring".
3. **Lead with the failures.** Codex missing traps, the database lock, the wrong
   "verified" claims. In 99P culture these make the report more credible.
