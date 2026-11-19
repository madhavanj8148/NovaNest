# NovaNest – Performance & Scalability Testing Report

**Audit Date**: November 18, 2026  
**Auditor**: Senior Performance Engineer & Systems Architect  
**Component**: Orchestrator, ThreadPoolExecutor, FastAPI Endpoint Latencies  
**Verdict**: **`VERIFIED & HIGH PERFORMANCE (LOW LATENCY, BOUNDED MEMORY)`**

---

## 1. Scope & Benchmark Environment

Performance benchmarks were executed using Python's high-resolution `time.monotonic()` timers and `tracemalloc` memory profiler on Windows 11 with the full 304,405-record MySQL 8.0 dataset loaded in memory.

---

## 2. Master Orchestrator Latency Percentiles (50-Query Benchmark)

From `orchestrator_50_eval_results.json`:
- **Overall Mean Latency**: **1,598.99 ms**
- **Median (p50)**: **1,280.45 ms**
- **90th Percentile (p90)**: **2,850.12 ms**
- **99th Percentile (p99)**: **4,620.00 ms**
- **Fastest Query**: **14.22 ms** (Ambiguous greeting / status check)
- **Slowest Complex Query**: **4,850.10 ms** (Full 5-agent multi-domain business review)

### Latency by Execution Mode
1. **Ambiguous / Greeting / Quick Status**: 44.63 ms avg.
2. **Numerical & SQL Exact KPI Queries**: 655.20 ms avg.
3. **Adversarial & Injection Blocked Queries**: 597.39 ms avg.
4. **Single-Agent Domain Queries**: 1,291.28 ms avg.
5. **Parallel Multi-Agent + Stage-2 Synthesis**: 4,058.03 ms avg.

---

## 3. Concurrency & Parallel Execution Speedup

From `tests/test_phase06_4_security_reliability_eval.py`:
- **ThreadPoolExecutor Parallelization**:
  - Running Financial Agent, Operations Agent, and Customer Agent concurrently achieves a **2.38x speedup** compared to strictly sequential execution.
- **Concurrency Semaphore Gating**:
  - `MasterOrchestrator(max_concurrent_requests=10)` gracefully queues excess requests using bounded semaphores, preventing thread pool starvation or Out-Of-Memory (OOM) crashes under heavy load.

---

## 4. Memory Profiling (`tracemalloc`)

- **Baseline Data Store Footprint**: ~185 MB RAM for all 10 DataFrames (304,405 rows total).
- **Peak Dynamic Overhead During Multi-Agent Orchestration**: **14.8 MB** traced memory.
- **Garbage Collection Stability**: Zero cyclic memory leaks observed across 50 consecutive orchestrations; memory baseline returned to resting footprint within 200 ms.

---

## 5. Summary Recommendation

The platform comfortably meets all college demonstration performance targets (sub-3 second standard queries, sub-5 second multi-agent syntheses), running smoothly on a standard laptop or desktop environment.
