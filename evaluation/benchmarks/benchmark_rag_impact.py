"""Compare policy-generation quality and latency with RAG enabled versus disabled."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]


def score(policy: dict, reference: dict, tolerance: float) -> tuple[bool, bool, float | None, float | None]:
    lower, upper = policy.get("min"), policy.get("max")
    valid = isinstance(lower, (int, float)) and isinstance(upper, (int, float)) and lower < upper
    if not valid:
        return False, False, None, None
    min_error, max_error = abs(lower - reference["min"]), abs(upper - reference["max"])
    matches = policy.get("parameter") == reference["parameter"] and min_error <= tolerance and max_error <= tolerance
    return True, matches, min_error, max_error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("RULE_ENGINE_URL", "http://127.0.0.1:8004"))
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation" / "fixtures" / "policy_reference_cases.json")
    parser.add_argument("--runs", type=int, default=10, help="Requests per case and mode")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=0, help="Allowed error for each reference bound")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "rag_impact_raw.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.warmup < 0 or args.tolerance < 0:
        parser.error("runs must be positive; warmup and tolerance cannot be negative")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        for mode, use_rag in (("without_rag", False), ("with_rag", True)):
            endpoint = f"{args.url.rstrip('/')}/policy"
            for _ in range(args.warmup):
                requests.post(endpoint, params={"use_rag": use_rag}, json=case["patient"], timeout=args.timeout)
            for run in range(1, args.runs + 1):
                started = time.perf_counter()
                try:
                    response = requests.post(endpoint, params={"use_rag": use_rag}, json=case["patient"], timeout=args.timeout)
                    policy = response.json() if response.content else {}
                    response.raise_for_status()
                    if "error" in policy:
                        raise ValueError(f"Rule Engine error: {policy['error']}")
                    valid, matches, min_error, max_error = score(policy, case["reference_policy"], args.tolerance)
                    status_code, error = response.status_code, ""
                except (requests.RequestException, ValueError) as exc:
                    policy, valid, matches, min_error, max_error, status_code, error = {}, False, False, None, None, "", str(exc)
                row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "case_id": case["id"], "run": run,
                       "mode": mode, "use_rag": use_rag, "latency_ms": round((time.perf_counter() - started) * 1000, 4),
                       "status_code": status_code, "valid_policy": valid, "matches_reference": matches,
                       "min_absolute_error": min_error, "max_absolute_error": max_error,
                       "parameter": policy.get("parameter", ""), "min": policy.get("min", ""), "max": policy.get("max", ""), "error": error}
                rows.append(row)
                print(f"{case['id']} {mode}: {row['latency_ms']:.2f} ms, reference_match={matches}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    if any(row["error"] for row in rows):
        raise SystemExit("One or more policy requests failed; inspect the CSV.")


if __name__ == "__main__":
    main()
