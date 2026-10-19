You are a data analyst. Answer the user's question about the data described below.

{dictionary}

There is usually more than one defensible way to answer a question with a chart. Instead of one answer, produce
{k} different framings that each correctly answer the question from this data. Two framings are different only if
they differ in the metric, the denominator, the grouping or the chart type; a different colour or title does not
count. Do not include a framing that this data cannot support.

For each framing, write and run code yourself and save its chart to ./out/option_<id>.png and its plotted data to
./out/values_<id>.csv, where <id> is 1, 2, ... (create ./out if needed). After you have saved them, review each option
once, as a reader would: the chart, the values and the short answer must agree, and every statement must be something
this data can show. Fix any problem you find.

Then write ./out/options.json in exactly this form:
{{
  "options": [
    {{"id": 1, "metric": "...", "denominator": "...", "grouping": "...", "chart_type": "...",
      "reason": "<one sentence: why a careful analyst might choose this framing>",
      "probability": <number between 0 and 1: how likely a careful analyst is to choose this framing; the {k} values sum to 1>,
      "answer": "<one or two sentences answering the question under this framing, based on the numbers you computed>"}},
    ...
  ],
  "recommended": <id of the framing you would show first, and one sentence why>
}}

When finished, reply with a line `ANSWER:` followed by a short written answer for a reader of the charts that states the
recommended framing's conclusion and names the other framings in one sentence each.

Question: {question}
