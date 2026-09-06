"""Summarise RAG retrieval effectiveness and latency."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def percentile(values: list[float], q: float) -> float:
    values = sorted(values); position = (len(values) - 1) * q
    low, high = int(position), min(int(position) + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "evaluation" / "results" / "rag_raw.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "rag_summary.csv")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as stream: rows = list(csv.DictReader(stream))
    successful = [row for row in rows if row["ok"].lower() == "true"]
    if not successful:
        raise ValueError("No successful RAG measurements")
    latencies = [float(row["latency_ms"]) for row in successful]
    hits = [row["source_hit_at_k"].lower() == "true" for row in successful]
    summary = {"requests": len(rows), "successful_requests": len(successful),
               "success_rate": round(len(successful) / len(rows), 4), "source_hit_at_k": round(sum(hits) / len(successful), 4),
               "mean_reciprocal_rank": round(statistics.mean(float(row["reciprocal_rank"]) for row in successful), 4),
               "mean_latency_ms": round(statistics.mean(latencies), 4), "median_latency_ms": round(statistics.median(latencies), 4),
               "p95_latency_ms": round(percentile(latencies, .95), 4)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary)); writer.writeheader(); writer.writerow(summary)
    print(summary)


if __name__ == "__main__":
    main()
