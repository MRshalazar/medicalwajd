"""Benchmark the Rust ZKP executable without starting the CDSS services."""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE = ROOT / "zkp_engine" / "target" / "release" / ("zkp_engine.exe" if os.name == "nt" else "zkp_engine")


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * q
    low, high = int(position), min(int(position) + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def run_once(engine: Path, value: int, lower: int, upper: int) -> tuple[dict, float]:
    request = {"value": value, "min": lower, "max": upper}
    started = time.perf_counter_ns()
    completed = subprocess.run(
        [str(engine)], input=json.dumps(request), text=True, capture_output=True, check=True
    )
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return json.loads(completed.stdout), elapsed_ms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=30, help="Measured runs per test case")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "zkp_raw.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.warmup < 0:
        parser.error("--runs must be positive and --warmup cannot be negative")
    engine = args.engine.resolve()
    if not engine.is_file():
        raise FileNotFoundError(f"ZKP executable not found: {engine}. Run `cargo build --release` in zkp_engine.")

    cases = [("below", 90, 110, 135), ("lower_boundary", 110, 110, 135),
             ("in_range", 122, 110, 135), ("upper_boundary", 135, 110, 135),
             ("above", 190, 110, 135)]
    rows: list[dict[str, object]] = []
    for name, value, lower, upper in cases:
        for _ in range(args.warmup):
            run_once(engine, value, lower, upper)
        timings = []
        for run in range(1, args.runs + 1):
            response, elapsed_ms = run_once(engine, value, lower, upper)
            expected = "NORMAL" if lower <= value <= upper else "ALERT"
            rows.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "case": name,
                         "run": run, "value": value, "min": lower, "max": upper,
                         "expected_status": expected, "actual_status": response.get("status"),
                         "verified": response.get("verified"), "latency_ms": round(elapsed_ms, 4)})
            timings.append(elapsed_ms)
        print(f"{name:15} mean={statistics.mean(timings):.2f} ms  p95={percentile(timings, .95):.2f} ms")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    failures = [row for row in rows if row["actual_status"] != row["expected_status"] or row["verified"] is not True]
    print(f"Wrote {len(rows)} measurements to {args.output}")
    if failures:
        raise SystemExit(f"{len(failures)} correctness checks failed")


if __name__ == "__main__":
    main()
