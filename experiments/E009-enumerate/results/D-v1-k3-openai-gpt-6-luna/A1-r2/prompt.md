You are a data analyst. Answer the user's question about the data described below.

Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

There is usually more than one defensible way to answer a question with a chart. Instead of one answer, produce
3 different framings that each correctly answer the question from this data. Two framings are different only if
they differ in the metric, the denominator, the grouping or the chart type; a different colour, title or style does
not count. Do not include a framing that this data cannot support. If the question as asked cannot be answered from
this data, say so in each framing's answer and let the framings show what this data can show instead.

For each framing, write and run code yourself and save its chart to ./out/option_<id>.png and its plotted data to
./out/values_<id>.csv, where <id> is 1, 2, ... (create ./out if needed). After you have saved them, review each option
once, as a reader would: its chart, its values and its short answer must agree, the numbers in the answer must be
traceable to its values file, and every statement must be something this data can show. Fix any problem you find.

Then save ./out/options.json as plain JSON (no code fences, no comments) in exactly this form:
{
  "options": [
    {"id": 1, "metric": "...", "denominator": "...", "grouping": "...", "chart_type": "...",
      "reason": "<one sentence: why a careful analyst might choose this framing>",
      "probability": <number between 0 and 1: how likely a careful analyst is to choose this framing; the 3 values should sum to about 1>,
      "answer": "<one or two sentences answering the question under this framing, based on the numbers you computed>"},
    ...
  ]
}

Save options.json before you reply. When finished, reply with a line `ANSWER:` followed by one sentence per framing,
in the order of options.json, stating what each framing shows. Do not recommend one framing over another.

Question: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
