"""Summarise end-to-end CDSS workflow benchmark results."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "evaluation" / "results" / "pipeline_raw.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "pipeline_summary.csv")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as stream: rows = list(csv.DictReader(stream))
    successful = [row for row in rows if row["ok"].lower() == "true"]
    if not successful: raise ValueError("No successful pipeline measurements")
    latencies = [float(row["latency_ms"]) for row in successful]
    summary = {"requests": len(rows), "successful_requests": len(successful), "success_rate": round(len(successful)/len(rows), 4),
               "mean_latency_ms": round(statistics.mean(latencies), 4), "median_latency_ms": round(statistics.median(latencies), 4),
               "min_latency_ms": round(min(latencies), 4), "max_latency_ms": round(max(latencies), 4)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary)); writer.writeheader(); writer.writerow(summary)
    print(summary)


if __name__ == "__main__": main()
