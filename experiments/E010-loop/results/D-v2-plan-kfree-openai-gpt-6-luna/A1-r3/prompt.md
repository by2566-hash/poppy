You are a data analyst. Answer the user's question about the data described below.

Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

There is usually more than one defensible way to answer a question with a chart. Instead of one answer, produce
as many as a careful analyst would consider defensible, and no more (usually two to five) different framings that each correctly answer the question from this data. Include a framing only if a careful
analyst would consider it defensible; do not pad the list. Two framings are different only if
they differ in the metric, the denominator, the grouping or the chart type; a different colour, title or style does
not count. Do not include a framing that this data cannot support. If the question as asked cannot be answered from
this data, say so in each framing's answer and let the framings show what this data can show instead.

For each framing, where <id> is 1, 2, ... (create ./out if needed), work in this order before you write its analysis code:
1. Plan. Write the framing's initial plan to ./out/plan_<id>.json: whether this data can answer the question under this
   framing (yes, partly or no, and which part), the metric, the denominator, the population (which crashes or people are
   counted), the filters, the years and the grouping. Use the description above; do not query the data for this step.
2. Data check. With code, check only the columns and years in the plan, and only which rows the plan would use: the number
   of rows in the plan's population and years, and per year; for each column the plan filters on, groups by or sums, how
   many of those rows have the value missing in any form (NULL, an empty string, a word that stands for unknown, an
   impossible value) or piled up at a default value; and any year the file covers only in part. Save each fact as one row
   of ./out/check_<id>.csv with the columns fact and value. Then add to the plan file what these facts mean for the plan
   (which rows it would drop or count differently, and what population it then really counts) and what you decide for
   each: keep the rows and disclose them, exclude them, or show them as their own group. You may change the plan here;
   say what you changed and why.
3. Final plan. Write the final plan to the plan file, with a limitations entry filled from the data check.
These three steps are about which rows are used, never about results: do not compute or write any injury or death
number, or any sum, rate or share of an outcome, in them.

Then write and run the analysis code for the final plan and save its chart to ./out/option_<id>.png and its plotted
data to ./out/values_<id>.csv. The chart title states the final plan's metric and population; a subtitle or footnote
states its main limitation. After you have saved them, review each option
once, as a reader would: its chart, its values and its short answer must agree, the numbers in the answer must be
traceable to its values file or its check file, the code, chart title and interpretation must follow the final plan,
and every statement must be something this data can show. Fix any problem you find.

Then save ./out/options.json as plain JSON (no code fences, no comments) in exactly this form:
{
  "options": [
    {"id": 1, "metric": "<final plan>", "denominator": "<final plan>", "grouping": "<final plan>", "chart_type": "...",
      "reason": "<one sentence: why a careful analyst might choose this framing>",
      "probability": <number between 0 and 1: how likely a careful analyst is to choose this framing; the values should sum to about 1>,
      "answer": "<one sentence: the conclusion under this framing, based on the numbers you computed>",
      "interpretation": "<three or four sentences about the user's question: which part of the question this framing answers and what its chart shows about that part; why this framing is a defensible way to answer that part; which part of the question it leaves unanswered; and the data check: which rows the final plan does not use or counts differently and why, with the counts or shares from its check file, and what you decided about them>"},
    ...
  ]
}

Save options.json before you reply. When finished, reply with a line `ANSWER:` followed by one sentence per framing,
in the order of options.json, stating what each framing shows. Do not recommend one framing over another.

Question: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
