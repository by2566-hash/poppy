"""Shared pieces for the mimo stability screen (E006)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PARQUET = PROJECT / "data" / "processed" / "nyc_crashes.parquet"
import os
MODEL = os.environ.get("POPPY_MODEL", "mimo-v2.6-flash-free")  # override: POPPY_MODEL=nemotron-3-ultra-free

# The team's six clear questions (phase-1 proposal), window 2013-2025.
QUESTIONS = {
    "P1": "How many people died in recorded motor vehicle crashes in NYC each year from 2013 to 2025?",
    "P2": "How many cyclists were injured in NYC each year from 2013 to 2025?",
    "P3": "How do pedestrian injuries compare across NYC boroughs from 2013 to 2025? Keep crashes with an unknown borough as their own group.",
    "P4": "How are NYC crashes distributed across the hours of the day, 2013 to 2025?",
    "P5": "What are the 10 most frequently recorded contributing factors for the first vehicle in NYC crashes, 2013 to 2025?",
    "P6": "How do the annual injury trends for cyclists and pedestrians in NYC compare, 2013 to 2025?",
    # Ambiguous (P7-P8) and insufficient-evidence (P9-P10), team proposal wording
    "P7": "Did traffic safety in NYC improve from 2013 to 2025? Make a visualization suitable for a news report and summarize the main findings.",
    "P8": "Which NYC borough was the most dangerous for pedestrians from 2013 to 2025? Compare the boroughs with a chart and give a conclusion suitable for a news report.",
    "P9": "Did the risk of a cyclist being injured or killed per ride in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.",
    "P10": "Assume a traffic safety policy started in NYC in 2018. Did it cause traffic deaths to decline afterward? Make a chart and explain based on this crash data.",
}

DATA_DICTIONARY = """Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available."""

PROMPT_A = """You are a data analyst. Answer the user's question about the data described below.

{dictionary}

Reply in exactly this format and nothing else:
1. One ```python code block that reads the data, computes the answer, saves the chart to ./out/initial.png and saves the plotted data to ./out/values.csv (create ./out if needed).
2. Then a line `ANSWER:` followed by a short written answer for a reader of the chart.

Question: {question}"""
