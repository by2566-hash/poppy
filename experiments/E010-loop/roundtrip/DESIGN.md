# Round trip: values.csv-only reverse inference (T3)

Implements `docs/v2-design-2026-11-07.md` §4 step 1–2. Built 2026-11-19; **smoke-tested only** (4 options). The full measurement is T5 and has not been run.

## Condition (cleared context, stripped input)

| Shown to the inferring model | Withheld |
|---|---|
| the option's `values_<id>.csv`: header and rows (first 200 rows), inlined in the prompt | the asked question and its id |
| the row count | chart, chart title, answer, interpretation |
| | code, plan and check files, data dictionary, source data |
| | every file name (the sandbox holds only the read-only permission config) |

- One fresh sandbox and one fresh OpenCode session per guess; hermetic switches on (`call_model`).
- Read-only permissions (`opencode.review.json`); `tool_calls` is recorded and should be 0.
- Model: `POPPY_MODEL` (default GPT-6 Luna in a fresh context, the fallback of FOLLOWUPS §3 decision 4). A non-generator model is a T5 option.
- Prompt: `reverse_prompt.md`, sha `7f659893f3fc…`. It names no dataset, place, trap or column.

## Guess format

JSON: `guessed_question` (one sentence), `metric`, `denominator`, `population`, `filters`, `grouping`, `time_window`, `confidence` (0–1), `not_recoverable`. Fields the table does not show are "not visible". One retry when the reply does not parse.

## Repeats and floors

- **N = 3 guesses per option** (proposed). Guesses are independent sessions.
- **Repeat floor** = mean pairwise distance among the N guesses of one option: the noise of the reverse step.
- **Reference scale** = distance among the three F2 phrasings of each pilot question (mpnet mean 0.069, max 0.141).
- **Between-option** distance (different options, same asked question) is printed for context; options are meant to differ.

## Distances (diagnostic only; Bo 2026-11-08)

- Cosine distance, asked question ↔ guessed question, with both local models (all-mpnet-base-v2, all-MiniLM-L6-v2).
- Reported twice: against the full asked text, and against the **core** question (text up to the first "?"), because pilot prompts append a task sentence ("Make a chart …").
- Ratio = asked→guess / repeat floor.
- Whether an option answers a different question is the judge's call (T4), from the structured fields. No field matching is done here.

## Output for the judge (T4)

`results/<label>/guesses.jsonl`, one row per option × guess:
`label, q, base, type, rep, option, guess_n, asked_question, values_file, values_sha, n_rows, header, leak_tokens, guess{…}, parsed, model, prompt_sha, tool_calls, errors, distances{asked_guess_*, core_guess_*, repeat_floor_*}`.
Per call: `results/<label>/records/<q>-r<rep>-o<opt>-g<n>/{prompt.md, response.md, meta.json}` (no secrets). The judge must not be given `distances`.

## Limits

1. **Column names are part of the table.** They are written by the generator and carry meaning (`motorist_deaths_per_100k_crashes`). They are shown, since they are what the option delivers; `leak_tokens` records the asked-question words found in the header or labels. A generator could close the distance by naming columns after the question (Goodhart; the generator never sees this metric).
2. **The opposite also happens.** 34 of 484 values files in the E010 arms have a generic measure column (`value`, `total`, `count`, `metric`). The guess then cannot recover the measure, and the distance is large for a reason unrelated to substitution.
3. **Some of the question is never in a table**: place (NYC), intent words ("safer", "risk", "decline"), the data source. Absolute distances are therefore far above the paraphrase scale even for a faithful option (smoke test: 0.29–0.59 vs 0.07). Only relative comparisons between arms, and the ratio, are meaningful.
4. The repeat floor of one model in one prompt is small (0.002–0.16 in the smoke test), so ratios are large and unstable. Whether to use the per-option floor or a pooled floor is open.
5. Only the first values file of an option is used (D options have exactly one).
6. Same model family as the generator unless `POPPY_MODEL` is changed.

## Open questions for Bo

- Is the core question (task sentence removed) the right reference text?
- Floor: per-option or pooled across the label?
- Should options with a generic measure column be reported separately (limit 2)?
- Second inferring model for T5, or Luna only?
