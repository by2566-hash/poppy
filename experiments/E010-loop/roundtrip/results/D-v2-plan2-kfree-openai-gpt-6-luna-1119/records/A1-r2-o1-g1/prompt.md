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

year,total,eligible_brooklyn_crash_records
2013,3641,47024
2014,3349,47761
2015,3029,50851
2016,2917,47464
2017,2663,44915
2018,2785,47313
2019,2700,44479
2020,1781,25473
2021,1905,25174
2022,2275,23369
2023,2385,22890
2024,2645,22785
2025,2835,24303
