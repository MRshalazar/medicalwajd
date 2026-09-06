"""Benchmark complete CDSS workflow requests against a running coordinator."""
from __future__ import annotations

import argparse
import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]


def request_pipeline(base_url: str, patient_id: str, timeout: float) -> dict:
    started = time.perf_counter()
    try:
        response = requests.get(f"{base_url.rstrip('/')}/run/{patient_id}", timeout=timeout)
        payload = response.json() if response.content else {}
        response.raise_for_status()
        return {"ok": True, "status_code": response.status_code, "latency_ms": (time.perf_counter()-started)*1000,
                "proof_status": payload.get("proof", {}).get("status"), "decision": payload.get("decision", {}).get("stable")}
    except (requests.RequestException, ValueError) as exc:
        return {"ok": False, "status_code": None, "latency_ms": (time.perf_counter()-started)*1000,
                "proof_status": None, "decision": None, "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("LANGGRAPH_URL", "http://127.0.0.1:8007"))
    parser.add_argument("--patient-id", default="10009628")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "pipeline_raw.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.concurrency < 1: parser.error("runs and concurrency must be positive")
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(request_pipeline, args.url, args.patient_id, args.timeout) for _ in range(args.runs)]
        rows = []
        for run, future in enumerate(as_completed(futures), 1):
            row = {"run": run, "url": args.url, "patient_id": args.patient_id, "concurrency": args.concurrency, **future.result()}
            rows.append(row); print(f"run {run}: {row['latency_ms']:.2f} ms ({'ok' if row['ok'] else row.get('error')})")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["run", "url", "patient_id", "concurrency", "ok", "status_code", "latency_ms", "proof_status", "decision", "error"]
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    if not all(row["ok"] for row in rows): raise SystemExit("One or more pipeline requests failed; inspect the CSV.")


if __name__ == "__main__": main()
