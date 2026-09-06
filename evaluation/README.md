# Evaluation Suite

This folder evaluates the measurable parts of the Privacy-Preserving CDSS. All
benchmark outputs are written to `evaluation/results/` and are intentionally
ignored by version control so each experiment remains reproducible.

## Prerequisites

Build the ZKP executable once:

```powershell
cd zkp_engine
cargo build --release
cd ..
```

For end-to-end tests, start the system first:

```powershell
docker compose up --build -d
```

## Run the experiments

```powershell
# ZKP correctness and latency (five boundary/out-of-range cases, 30 runs each)
python evaluation/benchmarks/benchmark_zkp.py --runs 30
python evaluation/analysis/analyze_zkp.py

# ZKP throughput under increasing simultaneous clients
python evaluation/benchmarks/benchmark_scalability.py --requests 20 --clients 1 2 4 8

# End-to-end CDSS latency (requires the Docker services)
python evaluation/benchmarks/benchmark_pipeline.py --runs 10 --concurrency 1
python evaluation/analysis/analyze_pipeline.py

# RAG impact: retrieval latency and whether the correct guideline is returned
python evaluation/benchmarks/benchmark_rag.py --runs 10
python evaluation/analysis/analyze_rag.py

# RAG ablation: compare policy generation with and without retrieved context
python evaluation/benchmarks/benchmark_rag_impact.py --runs 10
python evaluation/analysis/analyze_rag_impact.py

# Whole-system validation across representative patient records
python evaluation/benchmarks/benchmark_system.py --runs 3
python evaluation/analysis/analyze_system.py

# Python-side memory allocations incurred by the proof client
python evaluation/profiling/profile_proof_memory.py --runs 30

# Optional PNG plots; install matplotlib first if it is not available
python evaluation/analysis/generate_figures.py
```

Use `--help` on each script to adjust the number of runs, service URL, output
path, or ZKP executable path. For a remote coordinator, set
`$env:LANGGRAPH_URL="http://HOST:8007"` or pass `--url`.

## Outputs

| File | Contents |
| --- | --- |
| `results/zkp_raw.csv` | Per-run ZKP response, expected status, and process latency |
| `results/zkp_summary.csv` | Correctness rate plus mean/median/p95 latency by test case |
| `results/scalability_raw.csv` | Throughput and latency at each client concurrency level |
| `results/pipeline_raw.csv` | Per-run coordinator latency and HTTP outcome |
| `results/pipeline_summary.csv` | End-to-end success rate and latency summary |
| `results/rag_raw.csv` | Per-query RAG latency, returned sources, and source rank |
| `results/rag_summary.csv` | RAG availability, source hit@3, MRR, and latency summary |
| `results/rag_impact_raw.csv` | Policy outputs and latency from paired RAG/no-RAG requests |
| `results/rag_impact_summary.csv` | Quality, bound-error, and latency deltas attributable to RAG |
| `results/system_raw.csv` | Per-patient whole-workflow validation and latency |
| `results/system_summary.csv` | Whole-system validation rate and latency summary |
| `results/proof_memory.txt` | Python wrapper allocation profile |

## RAG and whole-system evaluation

`benchmark_rag.py` uses the ground-truth queries in `fixtures/rag_cases.json`.
It evaluates whether the expected guideline PDF is present in the top three
retrieved chunks (`source_hit_at_k`) and how high it ranks
(`mean_reciprocal_rank`), alongside retrieval latency. The Knowledge MCP now
returns a backward-compatible `sources` field so this can be checked without
trying to infer a PDF from chunk text. Add clinically reviewed query/source
pairs to that fixture as the guideline corpus grows.

`benchmark_rag_impact.py` is the project-level RAG ablation. It sends each
case in `fixtures/policy_reference_cases.json` to the Rule Engine twice: once
with retrieved guideline context and once without it. It then compares JSON
validity, reference-policy match rate, bound error, and latency. The initial
reference policies mirror the project's current hypertension demo values; they
must be reviewed and replaced with clinician-approved targets before making
clinical claims. The no-RAG query option exists only to support this evaluation.

`benchmark_system.py` evaluates the complete patient → RAG-backed policy →
ZKP → decision workflow for multiple patients. A request passes only when every
stage is present, policy bounds are numeric and ordered, the proof is verified
with a valid status, and the final decision agrees with that status. It checks
integration correctness as well as end-to-end latency; it does not establish
clinical validity of LLM-generated limits.

## Important interpretation note

The current `zkp_engine` produces a valid Bulletproof range proof for a
64-bit unsigned value. However, it does **not** cryptographically bind that
proof to the supplied clinical `min` and `max` limits. The `NORMAL`/`ALERT`
status is calculated by ordinary comparison in `zkp_engine/src/main.rs` after
the generic proof verifies. Therefore these benchmarks measure the current
implementation accurately, but they must not be presented as evidence that a
clinical interval is enforced by the zero-knowledge proof itself.
