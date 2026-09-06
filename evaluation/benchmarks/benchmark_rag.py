"""Measure RAG retrieval latency and whether expected guideline sources are retrieved."""
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


def retrieve(base_url: str, query: str, timeout: float) -> dict:
    started = time.perf_counter()
    try:
        response = requests.get(f"{base_url.rstrip('/')}/guidelines/{query}", timeout=timeout)
        payload = response.json() if response.content else {}
        response.raise_for_status()
        documents = payload.get("guidelines", [])
        sources = payload.get("sources", [])
        if not isinstance(documents, list) or not isinstance(sources, list):
            raise ValueError("RAG response must contain guidelines and sources lists")
        return {"ok": True, "latency_ms": (time.perf_counter() - started) * 1000,
                "document_count": len(documents), "sources": sources, "error": ""}
    except (requests.RequestException, ValueError) as exc:
        return {"ok": False, "latency_ms": (time.perf_counter() - started) * 1000,
                "document_count": 0, "sources": [], "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("KNOWLEDGE_MCP_URL", "http://127.0.0.1:8010"))
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation" / "fixtures" / "rag_cases.json")
    parser.add_argument("--runs", type=int, default=10, help="Measured retrievals per query")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "rag_raw.csv")
    args = parser.parse_args()
    if args.runs < 1 or args.warmup < 0:
        parser.error("--runs must be positive and --warmup cannot be negative")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not cases:
        raise ValueError("The RAG case file contains no queries")

    rows = []
    for case in cases:
        query, expected = case["query"], case["expected_source"]
        for _ in range(args.warmup):
            retrieve(args.url, query, args.timeout)
        for run in range(1, args.runs + 1):
            result = retrieve(args.url, query, args.timeout)
            sources = result["sources"]
            rank = sources.index(expected) + 1 if expected in sources else 0
            row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "query": query,
                   "expected_source": expected, "run": run, "url": args.url, **result,
                   "sources": json.dumps(sources), "source_hit_at_k": rank > 0, "reciprocal_rank": 1 / rank if rank else 0}
            rows.append(row)
            print(f"{query}: {result['latency_ms']:.2f} ms, rank={rank or 'miss'}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    if not all(row["ok"] for row in rows):
        raise SystemExit("One or more RAG requests failed; inspect the CSV.")


if __name__ == "__main__":
    main()
