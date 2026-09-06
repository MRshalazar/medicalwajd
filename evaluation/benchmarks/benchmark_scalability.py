"""Measure ZKP throughput as concurrent clients increase."""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE = ROOT / "zkp_engine" / "target" / "release" / ("zkp_engine.exe" if os.name == "nt" else "zkp_engine")


def invoke(engine: Path, index: int) -> float:
    payload = {"value": 100 + (index % 60), "min": 110, "max": 135}
    started = time.perf_counter()
    subprocess.run([str(engine)], input=json.dumps(payload), text=True, capture_output=True, check=True)
    return (time.perf_counter() - started) * 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clients", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--requests", type=int, default=20, help="Total requests per client level")
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "scalability_raw.csv")
    args = parser.parse_args()
    engine = args.engine.resolve()
    if not engine.is_file(): raise FileNotFoundError(engine)
    rows = []
    for clients in args.clients:
        if clients < 1: parser.error("client counts must be positive")
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=clients) as pool:
            futures = [pool.submit(invoke, engine, index) for index in range(args.requests)]
            latencies = [future.result() for future in as_completed(futures)]
        wall_s = time.perf_counter() - started
        row = {"concurrent_clients": clients, "requests": args.requests, "wall_time_s": round(wall_s, 4),
               "throughput_rps": round(args.requests / wall_s, 3), "mean_latency_ms": round(sum(latencies) / len(latencies), 3),
               "max_latency_ms": round(max(latencies), 3)}
        rows.append(row); print(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


if __name__ == "__main__": main()
