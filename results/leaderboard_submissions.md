# Official Kaggle Leaderboard Submissions Log

Tracking official submissions for Project Graft to the [Google - The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent).

---

## Submission History

| Ref (ID) | Date (UTC) | Architecture & Description | Checksum (SHA256) | Dev30 Resolution | Status | Public Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`57407885`** | **2026-10-19 20:00:09** | **Project Graft: Paced Single-Agent (`recovered_v2`)**<br>- 9 local tools (AST + Graph + Filesystem)<br>- Strict 3.5m pacing ceiling & Stop-and-Submit<br>- `build/repro.py` isolation & pre-submission `rm` guardrail<br>- `thinking_budget: 1024`, `temperature: 0.1` | `d85be638e95e3f226bdfc7e047a8e3ae577b23d0e14b29d44414387f95b7e0d9` | **53.3% (16/30)** | **PENDING** | *Scoring* |
| `57364226` | 2026-10-18 18:02:13 | Graft v2: Time-aware pacing, 80 tool calls, 30s cmd timeout, build/ scratchpad isolation | `—` | 53.3% (16/30) | COMPLETE | 0.17 |
| `57302964` | 2026-10-17 08:16:01 | v1 baseline: 31B, single agent, no LoRA, all 9 tools, temp 1.0, thinking 2048 | `—` | 36.7% (11/30) | COMPLETE | 0.12 |

---

## Active Submission Specification (`57407885`)

- **Model**: `gemma-4-31b-it-qat-w4a16-ct`
- **Compiler**: `adk-submission` (0.2.13) conforming to `SandboxedAgentConfig` Pydantic schema
- **Archive Size**: 3.02 KB (< 100 KB budget limit; competition ceiling 3 GiB)
- **Included Files**:
  - `agent.yaml`
  - `eval_config.yaml`
  - `prompts/system.md`
- **Budget Envelopes**:
  - Max time per task: 6.0 minutes (operational ceiling 3.5 minutes)
  - Max tool calls per task: 80 calls
  - Single command timeout: 30 seconds
  - Generation config: `temperature: 0.1`, `top_p: 0.95`, `max_output_tokens: 8192`, `thinking_budget: 1024`
