"""Summarise the RAG policy-generation ablation experiment."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def boolean_rate(rows: list[dict], field: str) -> float:
    return sum(row[field].lower() == "true" for row in rows) / len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "evaluation" / "results" / "rag_impact_raw.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "rag_impact_summary.csv")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as stream: rows = list(csv.DictReader(stream))
    if not rows: raise ValueError("Input contains no measurements")
    summary = []
    for mode in ("without_rag", "with_rag"):
        group = [row for row in rows if row["mode"] == mode]
        if not group: raise ValueError(f"Missing {mode} measurements")
        errors = [float(row["min_absolute_error"]) + float(row["max_absolute_error"]) for row in group if row["min_absolute_error"]]
        summary.append({"mode": mode, "requests": len(group), "valid_policy_rate": round(boolean_rate(group, "valid_policy"), 4),
                        "reference_match_rate": round(boolean_rate(group, "matches_reference"), 4),
                        "mean_total_bound_error": round(statistics.mean(errors), 4) if errors else "",
                        "mean_latency_ms": round(statistics.mean(float(row["latency_ms"]) for row in group), 4)})
    baseline, rag = summary
    error_difference = ""
    if baseline["mean_total_bound_error"] != "" and rag["mean_total_bound_error"] != "":
        error_difference = round(rag["mean_total_bound_error"] - baseline["mean_total_bound_error"], 4)
    summary.append({"mode": "rag_minus_baseline", "requests": "", "valid_policy_rate": round(rag["valid_policy_rate"] - baseline["valid_policy_rate"], 4),
                    "reference_match_rate": round(rag["reference_match_rate"] - baseline["reference_match_rate"], 4),
                    "mean_total_bound_error": error_difference,
                    "mean_latency_ms": round(rag["mean_latency_ms"] - baseline["mean_latency_ms"], 4)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)
    for row in summary: print(row)


if __name__ == "__main__":
    main()
