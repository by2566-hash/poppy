#!/usr/bin/env python3
"""Check B runs against the B contract (inputs, outputs, boundaries) from their saved records.

  python3 check_contract.py <dir> [--issues-csv out.csv]
      <dir>: results/<B_label>  or  ../../../poppy-sandbox/E007/<B_label>

One row per item. Machine checks are decided here; the two human checks (invented issue? unflagged
change?) are left for the scorer. --issues-csv writes one row per review issue / UNVERIFIED item from
review.json, with empty label columns, so the review step (③) can be scored on its own.
"""
import csv, json, sys
from pathlib import Path

STEPS, SECS = 15, 600
FAILS_ITEM = {"skipped_no_A_answer", "review_failure", "revise_incomplete"}
RETRY = {"review_infra_failure", "revise_infra_failure"}


def checks(m):
    if m.get("b_state") in {"skipped_no_A_answer"} | RETRY:
        return {}
    c = {"review read-only": not m.get("review_side_effects"),
         "review in budget": m.get("review_steps", 0) <= STEPS and m.get("review_secs", 0) <= SECS,
         "review format": bool(m.get("review_parsed")),
         "CHART CHECK": bool(m.get("chart_check"))}
    if m.get("b_state") in ("revised", "revise_incomplete"):
        c |= {"revise finished": m["b_state"] == "revised",
              "CHANGES one per issue": bool(m.get("changes_match_issues")),
              "revise no network": not m.get("revise_net_calls"),
              "revise in budget": m.get("revise_steps", 0) <= STEPS and m.get("revise_secs", 0) <= SECS,
              "A's outputs intact": m.get("a_outputs_intact", True)}
    return c


def main():
    root = Path(sys.argv[1])
    rows = sorted(root.glob("*/meta.json"))
    if not rows:
        sys.exit(f"no */meta.json under {root}")
    bad_items = 0
    for p in rows:
        m = json.loads(p.read_text())
        bad = [k for k, ok in checks(m).items() if not ok]
        bad_items += bool(bad)
        print(f"{p.parent.name:8} {m.get('b_state', '?'):22} issues={m.get('n_issues', 0)} "
              f"unverified={m.get('n_unverified', 0)} changed_cols={m.get('values_changed_cols')}  "
              f"{'OK' if not bad else 'FAIL: ' + ', '.join(bad)}")
    print(f"\n{len(rows)} items, {bad_items} with a machine-checked contract failure. "
          f"Human checks per item: invented issue? unflagged change?")

    if "--issues-csv" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--issues-csv") + 1])
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["item", "section", "n", "text",
                        "label (real error / unsupported claim / invented / taste / correct UNVERIFIED / misrouted)", "note"])
            for p in rows:
                r = p.parent / "review.json"
                if not r.exists():
                    continue
                rv = json.loads(r.read_text())
                for i in rv["issues"]:
                    w.writerow([p.parent.name, "ISSUES", i["n"], i["text"], "", ""])
                for j, t in enumerate(rv["unverified"], 1):
                    w.writerow([p.parent.name, "UNVERIFIED", j, t, "", ""])
                if rv["verdict"] == "none":
                    w.writerow([p.parent.name, "ISSUES", 0, "NONE", "", ""])
        print("wrote", out)


if __name__ == "__main__":
    main()
