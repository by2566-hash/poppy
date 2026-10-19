#!/usr/bin/env python3
"""Does a model actually see an attached chart? (E005 procedure, reusable for any model.)

  POPPY_MODEL=openai/gpt-6-luna python3 scripts/check_model_vision.py

Attaches a known chart and asks three things only visible in the pixels, with an explicit NO_IMAGE escape.
Prints PASS if all three answers match. Runs in the review config (read-only, no code), so the model cannot
re-derive the chart from code. One image: a capability check, not an accuracy estimate.
"""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E006-mimo-screen"))
from common import MODEL  # noqa: E402
from run_screen import call_model  # noqa: E402

# K3 A-v1 r1 chart: grouped bars, motorist (blue) vs cyclist (orange), totals box "1377 / 277 / 5.0:1"
CHART = ROOT / "experiments" / "E007-pilot-prompts" / "results" / "A-v1" / "K3-r1" / "out" / "initial.png"
CONFIG = ROOT / "experiments" / "E007-pilot-prompts" / "config" / "opencode.review.json"
EXPECTED = {"legend_entries": 2, "cyclist_colour": "orange", "total_motorist": 1377}
PROMPT = """Look at the attached chart image. Answer from the pixels only. If no image is attached or you cannot see it,
reply exactly NO_IMAGE. Otherwise reply in exactly this JSON and nothing else:
{"legend_entries": <number of legend entries>, "cyclist_colour": "<colour of the cyclist bars, one word>",
 "total_motorist": <the 13-year motorist total printed in the totals box, as an integer>}"""


def main():
    sb = ROOT.parent / "poppy-sandbox" / "_vision" / MODEL.replace("/", "-")
    shutil.rmtree(sb, ignore_errors=True)
    sb.mkdir(parents=True)
    shutil.copy(CONFIG, sb / "opencode.json")
    shutil.copy(CHART, sb / "chart.png")
    r = call_model(sb, PROMPT, timeout=180, files=[sb / "chart.png"])
    text = r["text"].strip()
    print(f"model={MODEL} secs={r['secs']} tools={r['tool_calls']} errors={r['errors']}")
    print("reply:", text[:300])
    if "NO_IMAGE" in text:
        print("FAIL: model reports no image")
        return 1
    m = re.search(r"\{.*\}", text, re.S)
    try:
        got = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        got = {}
    ok = (got.get("legend_entries") == EXPECTED["legend_entries"]
          and str(got.get("cyclist_colour", "")).lower().startswith("orange")
          and int(got.get("total_motorist") or 0) == EXPECTED["total_motorist"])
    print("PASS: reads the image" if ok else f"FAIL: expected {EXPECTED}, got {got}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
