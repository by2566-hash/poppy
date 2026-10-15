Revise an analysis based on a reviewer's numbered issues.

Question:
{question}

Data description:
{dictionary}

Current code:
{code}

Current plotted values (values.csv):
{values}

Current written answer:
{answer}

Reviewer's issues:
{critique}

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
