"""Create PNG charts from evaluation CSVs (requires matplotlib)."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream: return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "evaluation" / "results")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "figures")
    args = parser.parse_args()
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("Install matplotlib to generate figures: pip install matplotlib") from exc
    args.output.mkdir(parents=True, exist_ok=True)
    zkp = args.results / "zkp_summary.csv"
    if zkp.exists():
        rows = read_rows(zkp)
        plt.figure(figsize=(8, 4)); plt.bar([r["case"] for r in rows], [float(r["mean_latency_ms"]) for r in rows])
        plt.ylabel("Mean latency (ms)"); plt.xlabel("Test case"); plt.title("ZKP proof latency"); plt.tight_layout()
        plt.savefig(args.output / "zkp_latency.png", dpi=200); plt.close()
    scale = args.results / "scalability_raw.csv"
    if scale.exists():
        rows = read_rows(scale)
        plt.figure(figsize=(7, 4)); plt.plot([int(r["concurrent_clients"]) for r in rows], [float(r["throughput_rps"]) for r in rows], marker="o")
        plt.xlabel("Concurrent clients"); plt.ylabel("Throughput (proofs/s)"); plt.title("ZKP scalability"); plt.grid(alpha=.3); plt.tight_layout()
        plt.savefig(args.output / "zkp_scalability.png", dpi=200); plt.close()
    pipeline = args.results / "pipeline_raw.csv"
    if pipeline.exists():
        rows = read_rows(pipeline)
        plt.figure(figsize=(7, 4)); plt.bar([int(r["run"]) for r in rows], [float(r["latency_ms"]) for r in rows])
        plt.xlabel("Completed request"); plt.ylabel("End-to-end latency (ms)"); plt.title("CDSS pipeline latency"); plt.tight_layout()
        plt.savefig(args.output / "pipeline_latency.png", dpi=200); plt.close()
    rag = args.results / "rag_summary.csv"
    if rag.exists():
        row = read_rows(rag)[0]
        labels = ["Source hit@3", "MRR", "Availability"]
        values = [float(row["source_hit_at_k"]), float(row["mean_reciprocal_rank"]), float(row["success_rate"])]
        plt.figure(figsize=(7, 4)); plt.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b"])
        plt.ylim(0, 1); plt.ylabel("Score"); plt.title("RAG retrieval effectiveness"); plt.tight_layout()
        plt.savefig(args.output / "rag_effectiveness.png", dpi=200); plt.close()
    rag_impact = args.results / "rag_impact_summary.csv"
    if rag_impact.exists():
        rows = {row["mode"]: row for row in read_rows(rag_impact)}
        modes = ["without_rag", "with_rag"]
        labels = ["Without RAG", "With RAG"]
        quality = [float(rows[mode]["reference_match_rate"]) for mode in modes]
        plt.figure(figsize=(7, 4)); bars = plt.bar(labels, quality, color=["#9e9e9e", "#4c78a8"])
        for bar, value in zip(bars, quality): plt.text(bar.get_x() + bar.get_width() / 2, max(value, .02), f"{value:.0%}", ha="center", va="bottom")
        plt.ylim(0, 1); plt.ylabel("Reference-policy match rate"); plt.title("Effect of RAG on policy quality"); plt.tight_layout()
        plt.savefig(args.output / "rag_policy_quality.png", dpi=200); plt.close()
        latency = [float(rows[mode]["mean_latency_ms"]) for mode in modes]
        plt.figure(figsize=(7, 4)); bars = plt.bar(labels, latency, color=["#9e9e9e", "#f58518"])
        for bar, value in zip(bars, latency): plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:,.0f} ms", ha="center", va="bottom")
        plt.ylabel("Mean latency (ms)"); plt.title("RAG policy-generation overhead"); plt.tight_layout()
        plt.savefig(args.output / "rag_policy_latency.png", dpi=200); plt.close()
    system = args.results / "system_raw.csv"
    if system.exists():
        rows = read_rows(system)
        plt.figure(figsize=(7, 4)); plt.bar(range(1, len(rows) + 1), [float(row["latency_ms"]) for row in rows])
        plt.xlabel("Validated workflow request"); plt.ylabel("End-to-end latency (ms)"); plt.title("Whole-system CDSS latency"); plt.tight_layout()
        plt.savefig(args.output / "system_latency.png", dpi=200); plt.close()
    print(f"Figures written to {args.output}")


if __name__ == "__main__": main()
