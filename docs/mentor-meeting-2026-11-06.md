# Mentor meeting 2026-11-06: record, analysis, and the next design step

- **Status:** record of the meeting (complete) + analysis + a proposal for phase 2b. The proposal is not decided; §7 lists the decisions for Bo.
- **Source:** LectMate transcript `Note_20261106_19-42-40_LectMate.txt` (about 18 min, noisy ASR: "arrow" = error, "Regive" = Rajeev, "objective" at 11:02 is meant as "subjective"). Deck: team "phase-2" Google Slides (F1 slide 2, F3 slides 3–5, F2 slides 6–10).
- **Present:** Ryan (mentor), the three of us. Rajeev mentioned, not speaking.

## 1. What we presented

| Time | Speaker | Content (as said, cleaned of ASR noise) |
|---|---|---|
| 00:15 | Bo | New phase, three parts: a new prompt; which question each chart actually answers; same questions in different words. |
| 00:39–02:38 | Bo, **F1** | D v1 (k = 3) vs D v2 (free k + interpretation: what each option answers, why it makes sense, its limits). 6 questions × 3 runs. v2 usually gives 2 options; a typical run takes 76 s, down from 96 s; steps unchanged. Silent errors: 24/54 options before, 14/42 after, but six questions are too few to show a clear gain. Part of the lower count comes from wording (K1), and the same prompt failed again under rephrasing. v2 changes the options and their explanations; the framing errors remain. Prevention needs something else (a data profile / plan check). |
| 02:47–04:53 | teammate, **F3** | Reverse inference: the output chart as input, the model asked what question it answers from the chart only. Specific questions (K1–K3): the inferred question matches. Broad questions (A1, A2): the agent picks one perspective ("how do you define danger": injuries). Missing data (I1, no miles driven): the chart is misleading on its own and the inferred question is a different question. Summary: clear questions align; ambiguous and insufficient ones expose narrower readings and substitutions. |
| 04:53–08:33 | Chloe, **F2** | Six questions, casual and formal wording, 3 runs each. Focus on A1 ("safer" is open): casual, the top option (45%) combines injuries and deaths; formal, 40% each to deaths and injuries. The tie matters: the two charts tell different stories, and showing only one biases the reader. Pattern: with k = 3 fixed the agent varied the chart type; with free k it keeps similar visuals and varies **what it measures**. Two things to evaluate: how the charts differ visually, and whether they give the reader different ways to answer the question. |

## 2. What Ryan said (complete)

| Time | Point |
|---|---|
| 08:39 | "A lot of work in a week, very impressive"; the inquiries are very interesting. |
| 08:51–09:08 | The inverse idea (take the output, run it back to the input, see what you get and what thoughts that creates) is very good. |
| 09:08–09:19 | The second part (understanding, interpretability and explainability of the context) is "very, very cool". |
| 09:29 | Team asks: which area should we explore in the next phase? |
| 09:44–10:21 | No single recommendation; a **spectrum**. Choose by what the team finds most interesting and by **what you want to talk about when you use this project to get a job**. Ryan and Rajeev are interested in both ends. |
| 10:21–10:42 | Career frame (repeated from earlier meetings): data roles in the near future will be heavily about **using data science to improve the quality of AI systems**; visualizing information is very important there. |
| 10:42–11:08 | **End 1, explainability / interpretability:** "twist the knob", make it create different things, then explain what the changes are. Less measurable, more subjective and fuzzy, "and that's okay". |
| 11:08–11:31 | **End 2, measurable:** quantify the two experiments (F2, F3) until differences can be measured; "I don't know if there is an answer", but it gives specific, measurable results. |
| 11:31–11:52 | His own taste: the fuzzy end is more interesting; that does not make him right. If you choose measuring: when the output changes, how do you measure it? |
| 11:52–12:37 | Concrete version: how do you put a number on the **drift between two natural-language outputs**? Question → chart; clear the context; chart → question; measure the difference between the input question and the new one. Many NL / **embedding** strategies measure the distance between two texts. |
| 12:55–13:25 | Team: word embeddings, as learned in class. Ryan: like a list of fruits; factorize them and see how close they are; do the same with the questions. Makes a lot of sense. |
| 13:27–13:51 | **Close the loop:** use the difference you identify to **change the prompt**, then check whether the distance in the newly generated chart increases or decreases. |
| 13:55–14:32 | Team: we want to find differences in the ablation section; in evaluation we add an **LLM judge to supplement the ground truth**, and two automatic evaluations come before the human assessment. Ryan: "I like the sound of that." |
| 14:37–14:54 | Next milestone: only the **final presentation** (memory of 2026-10-27: about Fri 2026-12-18 with posters, unconfirmed). |
| 14:54–16:54 | **Budget:** the team's API spend is about $5.95, "nothing", do not worry. Story: another project spent about $5,000 in one night generating a synthetic dataset with the most expensive model, against his advice; the $8 dataset made with a small model was better. He is alerted every $100. |
| 17:07–17:33 | Team: still working on the ablation experiments and on improving evaluation with an LLM judge. Ryan: sounds great. |
| 17:33 | Questions on Slack; next meeting at the normal Friday time. |

## 3. Analysis

1. **No direction change; one new axis.** Everything we presented was accepted. The new thing is Ryan's framing of the *next* phase as a choice between explaining change (fuzzy) and measuring change (drift metrics), with the closed loop (distance → prompt change → distance) as the natural continuation.
2. **The two ends are not exclusive in our system.** We already have the measurable spine for correctness (silent-error rate, two-pass grader at ≈ 0.98 agreement, keyed gold). What we lack is a measure of *meaning*: does an output answer the question asked, and how far does it move when a knob moves. Ryan's drift metric is exactly that missing measure. The interpretability end is what explains a measured drift (facets, the `interpretation` field, case studies such as the A1 tie). Recommended framing: **measurable spine, interpretable surface**.
3. **His example metric needs care before it can be trusted.**
   - *Surface-form confound:* embedding distance responds to wording. F2 already gives the noise floor: paraphrases with the same meaning. A drift metric is valid only if it separates paraphrase pairs (same meaning) from neighbouring-question pairs (per-mile vs per-crash; Brooklyn vs Brooklyn-assigned records) and from unrelated pairs. We have all three kinds of pairs on disk.
   - *Leakage:* the chart-only F3 trial includes the chart title, which usually restates the question (the A2 inferred question even recovered the exact window and the "complete counts" filter). The stripped condition (`values.csv` only, FOLLOWUPS §3) is the real test; chart-only is the ceiling.
   - *Repeat noise:* F2 showed that facet sets change across phrasings as much as across repeats of the same phrasing (Jaccard within ≈ across on all six questions). Every drift must be reported against the repeat floor (a signal-to-noise ratio), not as a raw distance.
   - *Goodhart in the closed loop:* optimizing round-trip distance rewards charts that restate the question in the title. The guard is the existing rule: keep a change only if the target improves **and** silent-error does not rise, measured in the stripped condition.
4. **F3's I1 finding is a real design insight.** The I1 chart, read without its text, answers "deaths per crash", while the written answer says per-mile risk cannot be determined. Charts travel without captions. This is in tension with decision 7 (qualifications count only in the written output): decision 7 is right for grading the *answer*, but a separate "standalone chart" check would capture what F3 saw.
5. **Chloe's tie observation is measurable.** When the top probabilities are close (A1 formal 0.40 / 0.40), presenting one chart hides a different story. That becomes a presentation rule (show every option within Δp of the top) and a metric (top-option flip rate under repeats and paraphrases; probability margin).
6. **Prevention is now justified by counts, not by taste.** Across all 180 scored options (g8), 80 have a silent error; the failure instances are TR05 35, unsupported claim 24, TR01 20, TR07 17, TR08 13, TR15 12, PERMILE 4, TR11 1, unsourced 1. TR05, TR01, TR08 and TR07 are all facts about the data the agent was never shown (NULL boroughs, the 2020 recording change, NULL killed counts in 2026, open data ≠ official toll). That is the trigger written in `docs/v2-plan.md` §8 for "data profile in context" and "plan declaration".
7. **The LLM judge we announced exists already**, but our second grader is a second Luna pass (repeat stability, not independence). Ryan's cost story points the same way as our calibration plan: a cheaper model can be the better tool, but only measurement shows it. Restoring the mimo (or another cheap model) second grader is both an independence fix and a cost-aware result worth showing.
8. **The 2026-10-27 probes are partly answered:** paraphrase robustness (F2: framing sets move no more than under repetition), interpretation-level sampling (F1 `interpretation` + facets), K (free k gives a median of 2, never above 3). Still open: "right answer, wrong reason" (reasoning faithfulness) and chart choice by reading task.

## 4. Where we stand (the boundary of the week that just ended, and what was parked)

**This week's boundary (team decision 2026-11-01, `experiments/E009-enumerate/FOLLOWUPS.md`):** three temporary experiments on arm D only (F1 free k + interpretation, F2 rephrasing, F3 reverse inference), under common rules: GPT-6 Luna, the 6 pilot questions, D v1 as the baseline, one change per variant, K = 3, effects reported as screens (MDE ≈ 48 points), prompts frozen before runs. Out of scope this week: any prevention treatment, the loop (E010), the held-out questions, new arms. Module decisions were to follow right after F1–F3.

| Item | Status 2026-11-06 |
|---|---|
| F1 | done: run, scored (g8), gold verified, facets coded (first pass) |
| F2 | done: run by Chloe, scored (g8), gold verified, facets coded; 34/36 complete |
| F3 | chart-only trial on the deck (slides 3–5); not in the repo; stripped condition, structured guess, validation labels not done |
| Scorer | v0 + second grader + review triage; grader g8; standard decisions 1–7 |
| Harness | D end rule frozen (FROZEN.md) |
| Human labels | none yet: `review.csv` waits on three labels; promotion of grader items blocked on them |

**Parked in `docs/v2-plan.md` (§8 and "Not in v0") and their status now:**

| Parked | Trigger in the plan | Now |
|---|---|---|
| data profile in context; plan declaration | framing failures top the count | **trigger met** (§3 point 6) |
| E010 loop iteration 1 (open coding ≥ 30, taxonomy, one change, paired re-run) | after F1–F3 | due now |
| held-out P1–P10 run | end of phase 2, frozen workflow and scorer | keep for the end |
| gold plan schema | a treatment needs a machine check of the framing itself | not yet |
| pandas-assertion claim checker | provenance misses a prose-number error | not triggered (unsourced 1/180) |
| figure introspection hook | a chart-encoding failure appears | not triggered |
| reviewer fault injection; B arm in phase 2 | B chosen as the workflow | not triggered |
| VisJudge-7B ranker | D needs automatic readability ranking | not triggered |
| second labeller + κ; gate script; Inspect AI; `score.json` | sheet outgrows one person | not triggered |
| Wilson intervals, pass^K, PPI-corrected estimate | close comparisons; ≥ 30 audit rows | audit rows: 15 waiting for labels |
| mechanical superlative check (decision 3) | — | deferred |
| mimo (independent) second grader | free quota reset | pending |
| Bo's pipeline-v2 (S0 PROFILE … S6 VERIFY, `docs/pipeline-v2-design.md`) | after phase 1 | S0 PROFILE is the candidate treatment below |

## 5. Proposal: phase 2b (2026-11-07 → final presentation)

**Thesis for the final:** *an evaluation layer that measures both whether an analysis agent's chart is correct and whether it answers the question that was asked, and a loop that uses those measures to change the agent.* Two tracks share one loop.

### Track M (measurable): question drift and alignment

- **M1. A drift metric that is validated before it is used.** Three levels, cheapest first:
  1. *Semantic:* sentence-embedding cosine between two questions (a local open-source embedding model; Sentence-BERT family), optionally BERTScore.
  2. *Structured:* the inferring model returns `{metric, denominator, grouping, population, time_window}` (F3 design decision 2); field agreement with the asked question. Interpretable, so it also feeds Track I.
  3. *Judgment:* a binary judge, "is the asked question a reasonable prompt for this output?", calibrated like the other grader items.

  **Validation set from data we have:** positives = F2 paraphrase pairs (same base) and original-vs-paraphrase; hard negatives = neighbouring questions (I1 per-mile vs per-crash; A1 Brooklyn vs Brooklyn-assigned; A2 frequency vs severity); easy negatives = different bases. A metric is accepted if it ranks paraphrases < neighbours < unrelated (AUC per contrast). This turns "fuzzy" into a number with a validity check.
- **M2. F3 done properly:** stripped (`values.csv` only) and full (chart + text) conditions; every option, not only the top one; an inferring model that is not the generator, or Luna in a fresh read-only sandbox; 30–40 options hand-labelled "answers the asked / a neighbouring / an unrelated question" (FOLLOWUPS §3 decision 5). Output per option: alignment verdict + drift scores + mismatch type.
- **M3. Drift under knobs, against the repeat floor:** F2 (phrasing) and F1 (k, interpretation) re-expressed as drift ratios: across-condition distance / within-condition distance. Option sets compared as probability-weighted distributions over facets (Jensen–Shannon), plus the top-option flip rate.

### Track I (interpretable): explain what a knob changes

- **I1.** The facet codebook (two first passes exist) reviewed and frozen; automated facet assignment by embedding clusters of the `interpretation` field, checked against the hand codes.
- **I2.** Case studies per knob: what moved, in which facet, and why (A1 tie; I1 substitution; K1 wording). This is the subjective end Ryan prefers, presented on top of the numbers that show the change is real.
- **I3.** Reasoning faithfulness (10-27 probe): does the `interpretation` agree with what the chart and values show? The grader items c1/c2 already measure this per option; report it as a faithfulness rate.

### The loop, iteration 1 (E010), shared by both tracks

- **Observed failure (counts, §3 point 6):** undisclosed data facts, 85 of 127 failure instances (TR05 35, TR07 17, TR01 20, TR08 13).
- **One change:** **data profile in context** (S0 PROFILE from `pipeline-v2-design.md`): a code-generated, trap-agnostic profile of the table (NULL share per column per year, rows per year, partial periods, the data dictionary's own statement that counts are police-reported records). It names no trap.
- **Prediction:** TR05, TR08 and TR07 fall on A1, A2 and K1; TR01 falls only partly, because a row-count drop in 2020 is visible but its cause is not; drift on ambiguous questions does not rise.
- **Re-run:** D v2 + profile, 6 questions × 3, scored by g8 and by the drift metric (stripped condition).
- **Keep rule:** the targeted failure count falls and no other criterion rises (plan §5), plus no rise in question drift.
- **Iteration 2 candidate:** a plan check (declare metric, denominator and population before running code), if TR01 and the substitutions (I1) remain.

### Timeline (final presentation assumed Fri 2026-12-18; to confirm)

| Week of | Work |
|---|---|
| 11-09 | decisions in §7; M1 metric + validation set; F3 stripped condition implemented; human labels for review.csv (Bo); mimo grader restored if the quota reset |
| 11-16 | E010 iteration 1 (profile) run and scored; M2 on F1/F2 outputs; facet codebook frozen |
| 11-23 (Thanksgiving) | analysis; iteration 2 decided (plan check or stop) |
| 11-30 | iteration 2 or held-out P1–P10 run with the frozen workflow and scorer |
| 12-07 | write-up: field guide, blog draft, poster, video |
| 12-14 | final presentation (Fri 12-18, to confirm) |

## 6. Roles (proposal)

| Owner | Work |
|---|---|
| Bo | eval layer and loop: M1 metric validation, scorer, E010, human labels, the final thesis |
| Chloe | F2 drift analysis (M3), facet codebook, the A1-tie presentation rule |
| F3 teammate | M2: stripped/full reverse inference, 30–40 alignment labels, commits the deck trial into the repo |

## 7. Decisions for Bo

1. **Route:** measurable spine with an interpretable surface (recommended), or one end only. Ryan: choose by team interest and what you want to say in interviews.
2. **Drift metric:** three levels (embedding, structured fields, binary judge), each validated on the paraphrase / neighbour / unrelated pairs before use (recommended); or embedding cosine alone.
3. **Embedding model:** local open-source (fits the open-source constraint, no cost) vs an API embedding.
4. **E010 iteration 1 treatment:** data profile in context (recommended, trigger met), or plan check first.
5. **Standalone-chart check:** add a grader item "the chart alone states its measure and key caveat" (from F3's I1 finding), or leave chart reading to F3 only.
6. **Presentation rule from the A1 tie:** show every option within Δp ≤ 0.10 of the top; report the top-option flip rate.
7. **Final date and team roles:** confirm 12-18 and the owners in §6.
8. Pending from 11-06: confirm the two TR08 rule cells (F1 v2 A2-r1 o1/o2) and the v1 K1-r3 o3 edge (decision 5 vs 7).
