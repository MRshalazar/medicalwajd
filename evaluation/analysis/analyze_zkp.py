"""Summarise raw ZKP benchmark measurements into a reproducible CSV."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def percentile(samples: list[float], q: float) -> float:
    samples = sorted(samples); pos = (len(samples) - 1) * q; low = int(pos); high = min(low + 1, len(samples) - 1)
    return samples[low] + (samples[high] - samples[low]) * (pos - low)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "evaluation" / "results" / "zkp_raw.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "zkp_summary.csv")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as stream: records = list(csv.DictReader(stream))
    if not records: raise ValueError("Input contains no measurements")
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records: groups[record["case"]].append(record)
    rows = []
    for case, group in groups.items():
        latencies = [float(row["latency_ms"]) for row in group]
        correct = sum(row["actual_status"] == row["expected_status"] and row["verified"].lower() == "true" for row in group)
        rows.append({"case": case, "samples": len(group), "correctness_rate": round(correct / len(group), 4),
                     "mean_latency_ms": round(statistics.mean(latencies), 4), "median_latency_ms": round(statistics.median(latencies), 4),
                     "p95_latency_ms": round(percentile(latencies, .95), 4), "min_latency_ms": round(min(latencies), 4), "max_latency_ms": round(max(latencies), 4)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    for row in rows: print(row)


if __name__ == "__main__": main()
