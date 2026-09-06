"""Validate and time complete CDSS workflows across multiple patients."""
from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATIENTS = ["10007795", "10007928", "10009628"]


def validate(payload: dict) -> str:
    patient, policy, proof, decision = (payload.get(key) for key in ("patient", "policy", "proof", "decision"))
    if not all(isinstance(value, dict) for value in (patient, policy, proof, decision)): return "missing workflow stage"
    if not patient.get("id") or not patient.get("condition"): return "invalid patient stage"
    if not isinstance(policy.get("min"), (int, float)) or not isinstance(policy.get("max"), (int, float)) or policy["min"] >= policy["max"]: return "invalid policy bounds"
    if proof.get("status") not in {"NORMAL", "ALERT"} or proof.get("verified") is not True: return "invalid proof result"
    if decision.get("stable") is not (proof["status"] == "NORMAL"): return "decision does not match proof status"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("LANGGRAPH_URL", "http://127.0.0.1:8007"))
    parser.add_argument("--patient-ids", nargs="+", default=DEFAULT_PATIENTS)
    parser.add_argument("--runs", type=int, default=3, help="Runs per patient")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "system_raw.csv")
    args = parser.parse_args()
    if args.runs < 1: parser.error("--runs must be positive")
    rows = []
    for patient_id in args.patient_ids:
        for run in range(1, args.runs + 1):
            started = time.perf_counter()
            try:
                response = requests.get(f"{args.url.rstrip('/')}/run/{patient_id}", timeout=args.timeout)
                payload = response.json() if response.content else {}
                response.raise_for_status()
                validation_error = validate(payload)
                row = {"ok": not validation_error, "status_code": response.status_code, "validation_error": validation_error,
                       "proof_status": payload.get("proof", {}).get("status"), "decision_stable": payload.get("decision", {}).get("stable"), "error": ""}
            except (requests.RequestException, ValueError) as exc:
                row = {"ok": False, "status_code": "", "validation_error": "", "proof_status": "", "decision_stable": "", "error": str(exc)}
            row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "patient_id": patient_id, "run": run, "url": args.url,
                   "latency_ms": round((time.perf_counter() - started) * 1000, 4), **row}
            rows.append(row); print(f"patient {patient_id}, run {run}: {row['latency_ms']:.2f} ms ({'ok' if row['ok'] else row['error'] or row['validation_error']})")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    if not all(row["ok"] for row in rows): raise SystemExit("One or more whole-system checks failed; inspect the CSV.")


if __name__ == "__main__":
    main()
