#!/usr/bin/env python3
"""Minimal OpenAI API connectivity check for GPT-6 Luna. Not an experiment run.

Usage:  .venv/bin/python scripts/check_openai_api.py
Reads OPENAI_API_KEY from the environment or poppy/.env (git-ignored), through the same loader the
experiment harness uses. Prints no part of the key. Exit 0 = key valid, model reachable, reply returned.

Steps: (1) key present, (2) the model is visible to this key, (3) one request "Reply with OK.".
"""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E006-mimo-screen"))
from common import load_env_file  # noqa: E402  (same .env loader as the harness; also runs on import)

MODEL = os.environ.get("POPPY_OPENAI_MODEL", "gpt-6-luna")   # OpenAI-side id; OpenCode calls it openai/gpt-6-luna

def main():
    load_env_file()
    if not os.environ.get("OPENAI_API_KEY"):
        print("FAIL  OPENAI_API_KEY missing: put OPENAI_API_KEY=... in poppy/.env (git-ignored) or export it")
        return 1
    print("OK    OPENAI_API_KEY present (value not shown)")

    import openai
    print(f"      openai SDK {openai.__version__}")
    client = openai.OpenAI(timeout=60, max_retries=1)

    try:
        m = client.models.retrieve(MODEL)
        print(f"OK    model {m.id} accessible")
    except openai.AuthenticationError:
        print("FAIL  key rejected (401): the key is invalid or revoked"); return 1
    except openai.NotFoundError:
        print(f"FAIL  model {MODEL} not found for this key (404)"); return 1
    except openai.APIConnectionError as e:
        print(f"FAIL  cannot reach the API: {type(e).__name__}"); return 1

    try:
        r = client.responses.create(model=MODEL, input="Reply with OK.")
    except openai.APIStatusError as e:
        print(f"FAIL  request rejected: HTTP {e.status_code} {type(e).__name__}"); return 1
    text = (r.output_text or "").strip()
    u = r.usage
    print(f"OK    response returned: {text[:40]!r} (status {r.status}, model {r.model}, "
          f"tokens in/out {getattr(u, 'input_tokens', '?')}/{getattr(u, 'output_tokens', '?')})")
    return 0 if text else 1

if __name__ == "__main__":
    sys.exit(main())
