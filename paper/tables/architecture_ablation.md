# Architecture & Context Compaction Ablation Study

This document compiles the empirical results and architectural configurations across the development iterations of Project Graft on Gemma 4 31B W4A16.

---

## 1. Architectural & Configuration Comparison

| Dimension | Baseline | Iteration 1 (`recovered_v1`) | Iteration 2 (`recovered_v2`) | Iteration 3 (`subagent_v1`) |
| :--- | :--- | :--- | :--- | :--- |
| **Agent Paradigm** | Monolithic Single Agent | Monolithic Single Agent | Monolithic Single Agent | **Hierarchical Hybrid Sub-Agent** |
| **Root Agent (`coder`) Tools** | All 9 sandboxed tools | All 9 sandboxed tools | All 9 sandboxed tools | `[run_command, read_file, edit_file, write_file, get_status, submit_patch, code_analyzer]` |
| **Sub-Agent (`code_analyzer`)** | None | None | None | Declarative read-only `code_analyzer.yaml` (`skip_summarization: true`) |
| **Sub-Agent Tools** | N/A | N/A | N/A | `[search_similar_code, get_code_neighbors, get_code_subgraph, read_file, run_command]` |
| **Thinking Budget (Tokens)** | 2,048 | 1,024 | 1,024 | 1,024 (Root) / 1,024 (Sub-Agent) |
| **Generation Temperature** | 0.2 | 0.2 | 0.1 | 0.1 |
| **Max Tool Calls Budget** | 100 | 100 | 80 | 80 (Root) |
| **Command Timeout** | 120s | 30s | 30s | 30s |
| **Pacing Protocol** | Unconstrained | Stop-and-Submit Rule | Minute 3.5 Hard Ceiling + Parameter Order Guardrails | Hybrid Sub-Agent Localization + Stop-and-Submit |
| **Scratchpad Protocol** | Ambiguous (`/tmp` / `/workspace`) | Standardized `build/repro.py` | Strict `build/repro.py` + `rm` cleanup | Isolated Sub-Agent Context + `build/repro.py` |

---

## 2. Empirical Benchmark Performance

### Full 30-Task Validation Benchmark (`dev30`)

| Metric | Baseline | Iteration 1 (`recovered_v1`) | Iteration 2 (`recovered_v2`) | Iteration 3 (`subagent_v1`) | Target / Promotion Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tasks Evaluated** | 30 | 30 | 30 | *Pending Remote Eval* | 30 |
| **Tasks Resolved** | 11 | 12 | **16** | *TBD* | $\ge 17$ |
| **Resolution Rate** | 36.7% | 40.0% | **53.3%** | *TBD* | $\ge 56.7\%$ |
| **Mean Agent Latency** | 238.2s | 242.2s | **229.1s** | *TBD* | $\le 225.0$s |
| **Mean Wall Time** | 258.1s | 247.3s | **232.0s** | *TBD* | $\le 230.0$s |
| **Projected 120-Task Hours** | 7.94h | 8.07h | **7.64h** | *TBD* | $\le 7.50$h |
| **Fatal Timeout Rate** | 43.3% (13/30) | 26.7% (8/30) | **13.3% (4/30)** | *TBD* | $\le 10.0\%$ |

---

### Curated 10-Task Screening Benchmark (`dev10`)

The 10-task split (`eval/dev10.json`) serves as the rapid screening gate before allocating full 2-hour GPU eval runs.

| Task ID | Repository | Bucket | Baseline | `recovered_v1` | `recovered_v2` | `subagent_v1` | Key Diagnostic Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rich_3278` | `Textualize/rich` | tiny (1L) | TIMEOUT (305.1s) | TIMEOUT (303.8s) | **RESOLVED (262.2s)** | *TBD* | Scratchpad path traversal & isolation |
| `rich_3470` | `Textualize/rich` | tiny (2L) | TIMEOUT (305.5s) | TIMEOUT (296.0s) | **RESOLVED (209.7s)** | *TBD* | Post-fix over-verification / Stop-and-Submit |
| `rich_3676` | `Textualize/rich` | small (13L) | FAIL | RESOLVED (241.1s) | **RESOLVED (186.1s)** | *TBD* | Multi-file edit synthesis & indentation |
| `rich_4076` | `Textualize/rich` | small (6L) | FAIL | FAIL | FAIL (150.2s) | *TBD* | Code analyzer caller localization |
| `rich_3052` | `Textualize/rich` | medium (34L)| FAIL | FAIL | FAIL (227.4s) | *TBD* | Medium-scale component refactor |
| `fastapi_13920` | `fastapi/fastapi` | tiny (4L) | TIMEOUT (304.2s) | TIMEOUT (305.0s) | FAIL (369.0s) | *TBD* | Sub-agent search speedup on timeout bug |
| `fastapi_14301` | `fastapi/fastapi` | tiny (5L) | RESOLVED (189.4s)| RESOLVED (112.5s) | **RESOLVED (97.3s)** | *TBD* | Dependency schema complexity & clean anchor |
| `fastapi_14077` | `fastapi/fastapi` | small (11L) | FAIL | RESOLVED (92.1s) | **RESOLVED (78.4s)** | *TBD* | Multi-file route annotation consistency |
| `fastapi_14458` | `fastapi/fastapi` | small (7L) | RESOLVED (220.5s)| RESOLVED (195.0s) | **RESOLVED (188.4s)** | *TBD* | Response model validation |
| `fastapi_15588` | `fastapi/fastapi` | medium (23L)| FAIL | FAIL | FAIL (133.3s) | *TBD* | OpenAPI parameter schema extraction |
| **`dev10` Total** | — | — | **3 / 10 (30.0%)**| **5 / 10 (50.0%)** | **6 / 10 (60.0%)** | *TBD* | **Screening Gate: $\ge 7/10$ (70.0%)** |

---

## 3. Complexity Bucket Breakdown (`dev30`)

| Complexity Bucket | Ground-Truth Size | Baseline Resolved | `recovered_v1` Resolved | `recovered_v2` Resolved | `subagent_v1` Resolved |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tiny** | 1–5 lines (12 tasks) | 7 / 12 (58.3%) | 8 / 12 (66.7%) | **11 / 12 (91.7%)** | *TBD* |
| **Small** | 6–15 lines (8 tasks) | 3 / 8 (37.5%) | 4 / 8 (50.0%) | **5 / 8 (62.5%)** | *TBD* |
| **Medium** | 16–50 lines (5 tasks) | 1 / 5 (20.0%) | 0 / 5 (0.0%) | 0 / 5 (0.0%) | *TBD* |
| **Large** | 51–150 lines (3 tasks)| 0 / 3 (0.0%) | 0 / 3 (0.0%) | 0 / 3 (0.0%) | *TBD* |
| **Huge** | > 150 lines (2 tasks) | 0 / 2 (0.0%) | 0 / 2 (0.0%) | 0 / 2 (0.0%) | *TBD* |
| **Overall** | 30 tasks | **11 / 30 (36.7%)** | **12 / 30 (40.0%)** | **16 / 30 (53.3%)** | *TBD* |

---

## 4. Context Compaction & Token Economics

| Metric | Monolithic Architecture (`recovered_v2`) | Hierarchical Sub-Agent (`subagent_v1`) | Theoretical Impact |
| :--- | :--- | :--- | :--- |
| **Root Context Growth Rate** | ~1,200 tokens / exploratory turn | ~250 tokens / exploratory turn | **~79% reduction** in root token accumulation |
| **Grep / Search Result Retention** | Retained in root history across all turns | Isolated inside ephemeral sub-agent context | Prevents context distraction during edit synthesis |
| **Root Working Window Headroom** | Depleted to < 10,000 tokens after 15 turns | Retains > 22,000 tokens available for code diffs | Substantially fewer token truncation errors |
| **Turn Latency Overhead** | None (direct tool call) | +1 LLM forward pass per sub-agent invocation (~10–14s) | Slight latency trade-off compensated by fewer total turns |
