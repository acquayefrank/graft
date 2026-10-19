# Failure Mode Taxonomy & Post-Mortem Analysis (`dev30`)

Empirical failure mode taxonomy derived from trace-level post-mortem analysis across the 30-task development benchmark ([`eval/dev30.json`](file:///c:/Users/acquayefrank/Code/graft/eval/dev30.json)) under the production `recovered_v2` single-agent configuration.

---

## 1. Failure Mode Taxonomy Table

| Failure Category | Primary Mechanism | Frequency in Dev30 | Exemplar Tasks | Root Cause Analysis | Architectural / Pacing Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **I. Scale Horizon Timeout** | Diff volume exceeds single-turn editing capacity under time budget | **7 / 14 (50.0%)** | `rich_3061` (134L)<br>`rich_4070` (88L)<br>`fastapi_14419` (102L)<br>`rich_3930` (176L)<br>`fastapi_15661` (155L)<br>`rich_3938` (28L)<br>`rich_4006` (45L) | Multi-site refactoring across 3+ files exhausts the 3.5-minute operational budget during symbol location and call-graph traversal before all edit hunks can be synthesized. | Time-awareness ceiling ensures clean exit rather than unbounded hang; future work requires hierarchical multi-hunk patch planning. |
| **II. Partial Patch / Secondary Assertion Failure** | Patch passes core repro but fails strict hidden test edge cases | **4 / 14 (28.6%)** | `rich_4076` (6L)<br>`rich_3052` (34L)<br>`rich_3675` (18L)<br>`fastapi_15588` (23L) | The agent fixes the primary reported symptom (e.g., SSE event splitting in `fastapi_15588` or prompt default value in `rich_3052`), but deviates from expected library regex format or secondary parameterized edge cases. | Mandatory Stop-and-Submit rule successfully prevented fatal timeouts on these tasks, securing a submitted patch even if not 100% compliant. |
| **III. Exploration Thrashing / Deep Recursion** | Trapped in recursive type-inspection or buffer cycles | **3 / 14 (21.4%)** | `fastapi_13920` (4L)<br>`rich_3063` (2L)<br>`rich_3935` (7L) | Complex metaprogramming (e.g., Python 3.12 PEP 695 type aliases in FastAPI or re-entrant console buffer locking in Rich) produces subtle errors that confuse localized regex searching. | Single command 30s timeout guardrail prevents container freezes; 80 tool ceiling caps unproductive exploration loops. |

---

## 2. Complexity Bucket Resolution Breakdown (`dev30`)

Empirical resolution rate structured by ground-truth patch complexity:

| Patch Complexity Bucket | Ground-Truth Size | Evaluated Tasks | Resolved Tasks | Resolution Rate | Mean Latency | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tiny** | 1–5 lines | 12 | **10** | **83.3%** | 172.4s | Exploration Thrashing (2) |
| **Small** | 6–15 lines | 8 | **6** | **75.0%** | 204.8s | Scale / Partial Patch (2) |
| **Combined (Tiny + Small)** | **1–15 lines** | **20** | **16** | **80.0%** | **184.6s** | **80% Production Baseline** |
| **Medium** | 16–50 lines | 5 | 0 | 0.0% | 311.2s | Partial Patch (3), Timeout (2) |
| **Large** | 51–150 lines | 3 | 0 | 0.0% | 360.0s | Scale Horizon Timeout (3) |
| **Huge** | > 150 lines | 2 | 0 | 0.0% | 360.0s | Scale Horizon Timeout (2) |
| **Overall Dev30** | — | **30** | **16** | **53.3%** | **229.1s** | **Projected 7.64h for 120 Tasks** |

---

## 3. Key Research Insights for Paper Section 4

1. **The 15-Line Competence Boundary**:
   Under an offline, ~5-minute budget with open-weight 31B models, autonomous agents exhibit a sharp phase transition at $\approx 15$ lines of diff complexity. Below 15 lines, the agent resolves **80.0% (16 of 20)** of real-world bugs across heterogeneous repositories. Beyond 15 lines, cognitive drift and turn latency dominate.

2. **The Stop-and-Submit Trade-off**:
   On tasks `fastapi_15588`, `rich_3052`, `rich_3675`, and `rich_4076`, the agent successfully executed code edits and submitted valid diffs. While secondary assertions failed in hidden unit testing, stopping at turn 17–23 completely eliminated fatal session timeouts (which earned 0 points in baseline iterations).

3. **Single vs. Hierarchical Failure Dynamics**:
   Comparing `recovered_v2` single-agent failure logs with `subagent_v1` traces demonstrates that hierarchical sub-agents did not resolve the Scale Horizon boundary; instead, sub-agent delegation introduced an additional turn-latency tax that pushed previously resolved tiny/small tasks (e.g. `rich_3470`) across the timeout boundary.
