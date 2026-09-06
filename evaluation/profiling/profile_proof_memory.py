"""Profile Python-side allocations while invoking the ZKP executable.

This reports allocations in the benchmarking client, not peak native memory used by
the Rust process. Use an OS profiler for native process memory if required.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE = ROOT / "zkp_engine" / "target" / "release" / ("zkp_engine.exe" if os.name == "nt" else "zkp_engine")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "results" / "proof_memory.txt")
    args = parser.parse_args()
    engine = args.engine.resolve()
    if not engine.is_file(): raise FileNotFoundError(engine)
    payload = json.dumps({"value": 122, "min": 110, "max": 135})
    tracemalloc.start()
    for _ in range(args.runs):
        subprocess.run([str(engine)], input=payload, text=True, capture_output=True, check=True)
    current, peak = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot(); tracemalloc.stop()
    report = [f"runs: {args.runs}", f"python_current_bytes: {current}", f"python_peak_bytes: {peak}", "", "top allocation locations:"]
    report.extend(str(stat) for stat in snapshot.statistics("lineno")[:10])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:4])); print(f"Wrote {args.output}")


if __name__ == "__main__": main()
