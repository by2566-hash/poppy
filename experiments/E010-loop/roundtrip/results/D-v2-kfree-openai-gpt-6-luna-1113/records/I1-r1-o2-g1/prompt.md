Below is a table of numbers. It is the complete output table of one data analysis. Someone asked a question in plain language, an analyst computed this table to answer it, and you see only the table: not the question, not the chart, not the written answer, not the code, not the source data.

Work out what question the table most plausibly answers. Use only the table (its column names, row labels and values). Do not use tools, do not look for other files, do not ask for more information.

Reply with one JSON object and nothing else:

{
  "guessed_question": "<one sentence, phrased as the person would have asked it>",
  "metric": "<what is measured, in the table's terms>",
  "denominator": "<what the measure is divided by, or 'none (a count)'>",
  "population": "<which records, people or places are covered>",
  "filters": "<restrictions you can see in the table, or 'none visible'>",
  "grouping": "<what the rows are split by>",
  "time_window": "<the period covered, or 'not visible'>",
  "confidence": <a number from 0 to 1: how sure you are of guessed_question>,
  "not_recoverable": "<what about the question cannot be told from the table alone, or 'nothing'>"
}

Write "not visible" for a field the table does not show. Do not invent a place, a period or a data source that the table does not show.

TABLE (13 data rows):

year,reported_crashes,motorist_deaths,motorist_deaths_per_100k_crashes
2013,203742,110,53.989850
2014,206046,109,52.900809
2015,217708,95,43.636430
2016,229833,72,31.327094
2017,231007,107,46.318943
2018,231564,98,42.320913
2019,211486,82,38.773252
2020,112918,139,123.098177
2021,110558,134,121.203350
2022,103887,116,111.659784
2023,96607,123,127.319966
2024,91316,111,121.555916
2025,85546,81,94.685900
