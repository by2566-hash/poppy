# Canonical Data Contract v0 (Poppy Customs Gate)

- **Date:** 2026-10-12
- **Status:** ENFORCED
- **Principle:** All pipeline inputs, intermediate step exchanges, and trace outputs must validate against these canonical schemas. Deterministic operations only; no unseeded randomness.

---

## 1. Input Customs Gate: `nyc_crashes` Table
All analytical operations target `nyc_crashes.parquet`. Key canonical columns:
- `crash_date`: DATE (2012-07-01 to 2026-06-11)
- `crash_time`: TIME
- `borough`: VARCHAR (nullable, ~30% NULL)
- `number_of_persons_injured`: INTEGER
- `number_of_persons_killed`: INTEGER (note: NULL in late frozen data)
- `number_of_pedestrians_injured`: INTEGER
- `number_of_pedestrians_killed`: INTEGER
- `number_of_cyclist_injured`: INTEGER
- `number_of_cyclist_killed`: INTEGER
- `number_of_motorist_injured`: INTEGER
- `number_of_motorist_killed`: INTEGER
- `vehicle_type_code1`: VARCHAR

---

## 2. Step 1 Artifact: `IntentCard`
Output of S1 (Clarify Intent):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["PROCEED", "PROCEED_WITH_STATED_ASSUMPTIONS", "ENUMERATE", "ASK"]
    },
    "resolved_slots": {
      "type": "object",
      "properties": {
        "entity": {"type": "string"},
        "metric_scope": {"type": "string"},
        "time_window": {"type": "array", "items": {"type": "string"}},
        "policy_event": {"type": "string"},
        "policy_date": {"type": "string"}
      }
    },
    "missing_slots": {
      "type": "array",
      "items": {"type": "string"}
    },
    "clarifying_question": {
      "type": ["string", "null"]
    }
  },
  "required": ["decision", "resolved_slots", "missing_slots", "clarifying_question"]
}
```

---

## 3. Step 2 Artifact: `AnalysisPlan`
Output of S2 (Analysis Plan). Can contain 1 to 3 candidate interpretations:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "minItems": 1,
  "maxItems": 3,
  "items": {
    "type": "object",
    "properties": {
      "interpretation_id": {"type": "string"},
      "interpretation_name": {"type": "string"},
      "metric": {
        "type": "object",
        "properties": {
          "numerator_expression": {"type": "string"},
          "filter_sql": {"type": ["string", "null"]}
        },
        "required": ["numerator_expression"]
      },
      "denominator_class": {
        "type": "string",
        "enum": ["none", "crash_count", "population", "exposure_unavailable"]
      },
      "temporal_grain": {
        "type": "string",
        "enum": ["year", "month", "week"]
      },
      "window": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 2,
        "maxItems": 2
      },
      "breakpoints": {
        "type": "array",
        "items": {"type": "string"}
      },
      "chart_type": {
        "type": "string",
        "enum": ["time_series_line", "indexed_multi_series"]
      },
      "stated_assumptions": {
        "type": "array",
        "items": {"type": "string"}
      }
    },
    "required": [
      "interpretation_id",
      "metric",
      "denominator_class",
      "temporal_grain",
      "window",
      "chart_type"
    ]
  }
}
```

---

## 4. Policy / TC Customs Gate: `TrapFlag`
Output of deterministic code rule engine (Trap Checker):
**Hard Rule:** The LLM cannot decide actions or trap flags. The Code Policy Engine decides trap triggers and actions based on exact column, window, and breakpoint rules.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "trap_id": {"type": "string"},
      "hook_phase": {
        "type": "string",
        "enum": ["plan_static", "data_dynamic"]
      },
      "severity": {
        "type": "string",
        "enum": ["CRITICAL_MISLEADING", "CAVEAT_REQUIRED", "ANNOTATION_REQUIRED"]
      },
      "enforced_action": {
        "type": "string",
        "enum": ["INJECT_VERTICAL_LINE", "EXCLUDE_PARTIAL_WINDOW", "ADD_UNATTRIBUTED_SERIES", "FORCE_SUBTITLE_CAVEAT"]
      },
      "message": {"type": "string"}
    },
    "required": ["trap_id", "hook_phase", "severity", "enforced_action", "message"]
  }
}
```

---

## 5. Step 4 Artifact: `Narrative`
Output of S4 (Explanation):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "headline": {"type": "string"},
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "claim_text": {"type": "string"},
          "referenced_numbers": {
            "type": "array",
            "items": {"type": "number"}
          },
          "cell_provenance": {"type": "string"}
        },
        "required": ["claim_text", "referenced_numbers", "cell_provenance"]
      }
    },
    "caveats": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "trap_id": {"type": "string"},
          "caveat_text": {"type": "string"}
        },
        "required": ["trap_id", "caveat_text"]
      }
    }
  },
  "required": ["headline", "claims", "caveats"]
}
```

---

## 6. Trace & Evaluation Record Contract
Every step output logs into `traces.jsonl`:
```json
{
  "run_id": "UUID-v4",
  "question_id": "T01 | T02 | T03",
  "split": "dev | test",
  "config_hash": "SHA256",
  "step": "S1 | S2 | TC | S3 | S4",
  "model": "string",
  "repeat_index": "1..5",
  "input_hash": "SHA256",
  "prompt_hash": "SHA256",
  "output_payload": {},
  "parse_ok": true,
  "rule_checks": {},
  "latency_ms": 1200,
  "tokens_in": 1500,
  "tokens_out": 220,
  "error": null,
  "source": "model | gold_oracle"
}
```
