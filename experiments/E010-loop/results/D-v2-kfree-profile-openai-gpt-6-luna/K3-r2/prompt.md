You are a data analyst. Answer the user's question about the data described below.

Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Data profile of ./data/crashes.parquet (computed by code from the file; descriptive only).

Rows: 2,269,187. crash_date from 2012-07-01 to 2026-06-11.

Rows per year:
2012: 100,545 | 2013: 203,742 | 2014: 206,046 | 2015: 217,708 | 2016: 229,833 | 2017: 231,007 | 2018: 231,564 | 2019: 211,486 | 2020: 112,918 | 2021: 110,558 | 2022: 103,887 | 2023: 96,607 | 2024: 91,316 | 2025: 85,546 | 2026: 36,424
Rows per month in 2012 (dates 2012-07-01 to 2012-12-31): 07: 16,992 | 08: 17,142 | 09: 16,535 | 10: 16,864 | 11: 15,889 | 12: 17,123
Rows per month in 2026 (dates 2026-01-01 to 2026-06-11): 01: 6,773 | 02: 6,492 | 03: 6,759 | 04: 6,665 | 05: 7,413 | 06: 2,322

Share of NULL values per column and year (%):
| column | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| borough | 22.8 | 23.4 | 24.1 | 24.9 | 33.3 | 38.1 | 35.6 | 35.2 | 34.7 | 34.7 | 33.8 | 32.0 | 28.6 | 19.9 | 23.9 |
| zip_code | 22.8 | 23.4 | 24.1 | 24.9 | 33.3 | 38.1 | 35.6 | 35.2 | 34.7 | 34.7 | 33.8 | 32.0 | 28.6 | 19.9 | 23.9 |
| latitude | 15.0 | 15.6 | 16.2 | 15.9 | 16.2 | 6.0 | 6.5 | 8.2 | 7.9 | 7.9 | 8.6 | 7.5 | 7.8 | 1.1 | 0.9 |
| longitude | 15.0 | 15.6 | 16.2 | 15.9 | 16.2 | 6.0 | 6.5 | 8.2 | 7.9 | 7.9 | 8.6 | 7.5 | 7.8 | 1.1 | 0.9 |
| location | 15.0 | 15.6 | 16.2 | 15.9 | 16.2 | 6.0 | 6.5 | 8.2 | 7.9 | 7.9 | 8.6 | 7.5 | 7.8 | 1.1 | 0.9 |
| on_street_name | 14.5 | 14.2 | 14.9 | 15.4 | 23.1 | 23.1 | 24.0 | 24.1 | 26.1 | 26.9 | 27.2 | 27.7 | 28.3 | 30.8 | 32.3 |
| cross_street_name | 14.5 | 14.2 | 14.9 | 15.4 | 42.6 | 52.4 | 50.4 | 50.7 | 52.8 | 53.8 | 53.0 | 51.5 | 48.4 | 40.5 | 46.2 |
| off_street_name | 97.1 | 97.4 | 96.8 | 96.5 | 79.5 | 77.0 | 76.3 | 75.9 | 73.9 | 73.1 | 72.8 | 72.3 | 71.7 | 69.2 | 67.7 |
| number_of_persons_injured | 0.0 | 0.0 | 0.0 | 0.0 | <0.1 | <0.1 | <0.1 | 0.0 | 0.0 | <0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| number_of_persons_killed | 0.0 | 0.0 | 0.0 | 0.0 | <0.1 | <0.1 | <0.1 | 0.0 | <0.1 | 0.0 | 0.0 | 0.0 | 0.0 | <0.1 | 24.4 |
| contributing_factor_vehicle_1 | 0.0 | 0.1 | 0.2 | 0.4 | 0.3 | 0.3 | 0.3 | 0.3 | 0.5 | 0.5 | 0.6 | 0.7 | 0.7 | 0.8 | 0.6 |
| contributing_factor_vehicle_2 | 10.7 | 11.4 | 13.1 | 12.0 | 14.0 | 14.3 | 15.0 | 15.7 | 21.8 | 22.6 | 23.5 | 23.1 | 23.9 | 24.8 | 23.8 |
| contributing_factor_vehicle_3 | 93.3 | 93.2 | 93.8 | 93.5 | 93.5 | 93.7 | 93.7 | 93.3 | 90.5 | 89.7 | 90.4 | 90.8 | 91.1 | 91.8 | 92.4 |
| contributing_factor_vehicle_4 | 98.6 | 98.6 | 98.7 | 98.7 | 98.6 | 98.7 | 98.7 | 98.6 | 97.4 | 97.2 | 97.5 | 97.5 | 97.6 | 97.9 | 98.1 |
| contributing_factor_vehicle_5 | 99.7 | 99.7 | 99.7 | 99.7 | 99.7 | 99.7 | 99.6 | 99.6 | 99.2 | 99.1 | 99.3 | 99.3 | 99.3 | 99.4 | 99.5 |
| vehicle_type_code1 | <0.1 | 0.1 | 0.4 | <0.1 | 1.3 | 0.6 | 0.6 | 0.7 | 1.0 | 1.1 | 1.4 | 1.6 | 1.7 | 1.7 | 1.9 |
| vehicle_type_code2 | 10.7 | 10.2 | 10.0 | 8.9 | 18.2 | 20.0 | 20.4 | 21.0 | 30.2 | 33.4 | 34.0 | 33.4 | 33.8 | 34.3 | 35.9 |
| vehicle_type_code3 | 93.3 | 93.2 | 93.7 | 93.4 | 94.0 | 94.0 | 94.0 | 93.6 | 91.1 | 90.4 | 91.1 | 91.4 | 91.7 | 92.4 | 93.1 |
| vehicle_type_code4 | 98.6 | 98.6 | 98.7 | 98.6 | 98.8 | 98.7 | 98.7 | 98.6 | 97.5 | 97.3 | 97.6 | 97.7 | 97.8 | 98.0 | 98.2 |
| vehicle_type_code5 | 99.7 | 99.7 | 99.7 | 99.7 | 99.7 | 99.7 | 99.7 | 99.6 | 99.3 | 99.2 | 99.3 | 99.3 | 99.3 | 99.4 | 99.5 |
No NULL values in any year: crash_date, crash_time, number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed, number_of_motorist_injured, number_of_motorist_killed, collision_id.

Columns (whole file, row level):
- crash_date (DATE): from 2012-07-01 to 2026-06-11
- crash_time (TIME): from 00:00:00 to 23:59:00
- borough (VARCHAR): 5 distinct non-NULL values: BRONX, BROOKLYN, MANHATTAN, QUEENS, STATEN ISLAND
- zip_code (VARCHAR): 236 distinct non-NULL values
- latitude (DOUBLE): min 0.0, max 43.344444
- longitude (DOUBLE): min -201.35999, max 0.0
- location (VARCHAR): 349,143 distinct non-NULL values
- on_street_name (VARCHAR): 23,332 distinct non-NULL values
- cross_street_name (VARCHAR): 25,404 distinct non-NULL values
- off_street_name (VARCHAR): 271,300 distinct non-NULL values
- number_of_persons_injured (INTEGER): min 0, max 43
- number_of_persons_killed (INTEGER): min 0, max 8
- number_of_pedestrians_injured (INTEGER): min 0, max 27
- number_of_pedestrians_killed (INTEGER): min 0, max 6
- number_of_cyclist_injured (INTEGER): min 0, max 4
- number_of_cyclist_killed (INTEGER): min 0, max 2
- number_of_motorist_injured (INTEGER): min 0, max 43
- number_of_motorist_killed (INTEGER): min 0, max 5
- contributing_factor_vehicle_1 (VARCHAR): 66 distinct non-NULL values
- contributing_factor_vehicle_2 (VARCHAR): 65 distinct non-NULL values
- contributing_factor_vehicle_3 (VARCHAR): 56 distinct non-NULL values
- contributing_factor_vehicle_4 (VARCHAR): 43 distinct non-NULL values
- contributing_factor_vehicle_5 (VARCHAR): 34 distinct non-NULL values
- collision_id (BIGINT): min 22, max 4905771
- vehicle_type_code1 (VARCHAR): 1,905 distinct non-NULL values
- vehicle_type_code2 (VARCHAR): 2,132 distinct non-NULL values
- vehicle_type_code3 (VARCHAR): 317 distinct non-NULL values
- vehicle_type_code4 (VARCHAR): 125 distinct non-NULL values
- vehicle_type_code5 (VARCHAR): 81 distinct non-NULL values

There is usually more than one defensible way to answer a question with a chart. Instead of one answer, produce
as many as a careful analyst would consider defensible, and no more (usually two to five) different framings that each correctly answer the question from this data. Include a framing only if a careful
analyst would consider it defensible; do not pad the list. Two framings are different only if
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
      "probability": <number between 0 and 1: how likely a careful analyst is to choose this framing; the values should sum to about 1>,
      "answer": "<one sentence: the conclusion under this framing, based on the numbers you computed>",
      "interpretation": "<two or three sentences about the user's question: which part of the question this framing answers and what its chart shows about that part; why this framing is a defensible way to answer that part; and which part of the question it leaves unanswered>"},
    ...
  ]
}

Save options.json before you reply. When finished, reply with a line `ANSWER:` followed by one sentence per framing,
in the order of options.json, stating what each framing shows. Do not recommend one framing over another.

Question: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
