# Official Kaggle Leaderboard Submissions Log

Tracking official submissions for Project Graft to the [Google - The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent).

---

## Submission History

| Ref (ID) | Date (UTC) | Architecture & Description | Checksum (SHA256) | Dev30 Resolution | Status | Public Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `57521582` | 2026-10-22 10:51:57 | Project Graft: Phase 7 Multi-Hunk Decomposition & Pre-Flight Syntax Check<br>- 9 local tools (AST + Graph + Filesystem)<br>- Sequential multi-hunk patch planning & deferred test runs<br>- Mandatory `python -m py_compile` pre-flight syntax check<br>- 1-strike `edit_file` fallback & Clean-Exit protocol<br>- 4.5m pacing ceiling & event-driven telemetry | `233647c2513357a3673bb1821d298d3631c28fb87f37feb64d531e0e7ae7b5c8` | 53.3% dev30 (evaluated on medium5) | **PENDING** | — |
| `57488978` | 2026-10-21 16:00:49 | Project Graft: Phase 6 Protocol Hardening<br>- 9 local tools (AST + Graph + Filesystem)<br>- Mandatory Clean-Exit protocol (`has_function_call=False` on turn after submit)<br>- 1-strike `edit_file` fallback to Python one-liner<br>- Event-driven telemetry checkpoints<br>- 4.5m pacing envelope & 30-call ceiling | `eef795a61640b075c3c55a5dfcd6c473cabecf6dc638e1f9147c344d3acb44ea` | 53.3% (16/30) | **ERROR** (Notebook Threw Exception) | — |
| **`57454091`** | **2026-10-20 21:51:18** | **Project Graft: Paced Single-Agent (`recovered_v2` recalibrated)**<br>- 9 local tools (AST + Graph + Filesystem)<br>- Recalibrated 4.5m pacing ceiling & 30-call trigger<br>- Status telemetry check at Turn 15<br>- Mandatory Stop-and-Submit rule<br>- `build/repro.py` isolation & pre-submission `rm` guardrail | `9a5cf4920ca919d7a214d89a06192e6150edecad655e559ae0f6f227b68c333e` | **53.3% (16/30)** | **COMPLETE** | **0.17** |
| `57407885` | 2026-10-19 20:00:09 | Project Graft: Paced Single-Agent (`recovered_v2`)<br>- 9 local tools (AST + Graph + Filesystem)<br>- Strict 3.5m pacing ceiling & Stop-and-Submit<br>- `build/repro.py` isolation & pre-submission `rm` guardrail<br>- `thinking_budget: 1024`, `temperature: 0.1` | `d85be638e95e3f226bdfc7e047a8e3ae577b23d0e14b29d44414387f95b7e0d9` | 53.3% (16/30) | COMPLETE | 0.15 |
| `57364226` | 2026-10-18 18:02:13 | Graft v2: Time-aware pacing, 80 tool calls, 30s cmd timeout, build/ scratchpad isolation | `—` | 53.3% (16/30) | COMPLETE | 0.17 |
| `57302964` | 2026-10-17 08:16:01 | v1 baseline: 31B, single agent, no LoRA, all 9 tools, temp 1.0, thinking 2048 | `—` | 36.7% (11/30) | COMPLETE | 0.12 |

---

## Active Public Submission (`57454091` - Score 0.17)

- **Model**: `gemma-4-31b-it-qat-w4a16-ct`
- **Compiler**: `adk-submission` (0.2.13) conforming to `SandboxedAgentConfig` Pydantic schema
- **Archive Size**: 3.01 KB
- **Checksum**: `9a5cf4920ca919d7a214d89a06192e6150edecad655e559ae0f6f227b68c333e`
- **Public Score**: **0.17** (Tied Rank 1034 / 3,387 teams)
- **Included Files**:
  - `agent.yaml`
  - `eval_config.yaml`
  - `prompts/system.md`
- **Budget Envelopes & Protocol Invariants**:
  - Max time per task: 6.0 minutes (operational hard ceiling 4.5 minutes)
  - Telemetry check: `get_status` at Turn 15
  - Tool calls emergency abort: 30 calls (eval config hard limit 80 calls)
  - Single command timeout: 30 seconds
  - Generation config: `temperature: 0.1`, `top_p: 0.95`, `max_output_tokens: 8192`, `thinking_budget: 1024`
