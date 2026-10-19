#!/usr/bin/env python3
"""Builds production single-agent submission.zip from submission/ directory.

Packages only the production single-agent assets:
  - agent.yaml
  - eval_config.yaml
  - prompts/system.md
Excludes experimental sub-agents and validates archive integrity and size (< 100 KB).
"""

import os
import sys
import zipfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
SUBMISSION_DIR = ROOT / "submission"
OUT_ZIP = ROOT / "submission.zip"

PRODUCTION_FILES = {
    "agent.yaml",
    "eval_config.yaml",
    "prompts/system.md",
}

EXPECTED_TOOLS = [
    "run_command",
    "read_file",
    "edit_file",
    "write_file",
    "search_similar_code",
    "get_code_neighbors",
    "get_code_subgraph",
    "get_status",
    "submit_patch",
]

# 1. Parse and validate submission/agent.yaml
agent_yaml_path = SUBMISSION_DIR / "agent.yaml"
if not agent_yaml_path.is_file():
    sys.exit(f"Error: {agent_yaml_path} does not exist.")

class IncludeLoader(yaml.SafeLoader):
    pass

def include_constructor(loader, node):
    rel_path = loader.construct_scalar(node)
    target = SUBMISSION_DIR / rel_path
    if not target.is_file():
        raise FileNotFoundError(f"!include file not found: {target}")
    return target.read_text(encoding="utf-8")

IncludeLoader.add_constructor("!include", include_constructor)

with open(agent_yaml_path, "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=IncludeLoader)

assert config.get("name") == "coder", f"Expected agent name 'coder', got {config.get('name')}"
assert config.get("model") == "gemma-4-31b-it-qat-w4a16-ct", f"Unexpected model {config.get('model')}"
tools = config.get("tools", [])
assert tools == EXPECTED_TOOLS, f"Tools mismatch. Expected {EXPECTED_TOOLS}, got {tools}"

# Optional Pydantic SandboxedAgentConfig validation if adk is available
try:
    from adk_submission.schema import SandboxedAgentConfig
    # Use IncludeLoader to resolve !include for schema validation
    raw_cfg = yaml.load((SUBMISSION_DIR / "agent.yaml").read_text(encoding="utf-8"), Loader=IncludeLoader)
    SandboxedAgentConfig.model_validate(raw_cfg)
    print("[OK] Validated schema against SandboxedAgentConfig Pydantic model.")
except ImportError:
    pass

# 2. Build submission.zip
if OUT_ZIP.is_file():
    OUT_ZIP.unlink()

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel_path in sorted(PRODUCTION_FILES):
        full_path = SUBMISSION_DIR / rel_path
        if not full_path.is_file():
            sys.exit(f"Error: Required production file missing: {full_path}")
        zf.write(full_path, rel_path)

# 3. Verify archive contents and size
with zipfile.ZipFile(OUT_ZIP, "r") as zf:
    namelist = set(zf.namelist())
    print("\n--- Production Archive Contents ---")
    for info in zf.infolist():
        print(f"  {info.filename:<35} {info.file_size:>6} B  (deflated: {info.compress_size:>6} B)")
    
    missing = PRODUCTION_FILES - namelist
    if missing:
        sys.exit(f"Error: Missing files in submission.zip: {missing}")
    
    extra = namelist - PRODUCTION_FILES
    if extra:
        sys.exit(f"Error: Unexpected files in production submission.zip: {extra}")

size_kb = OUT_ZIP.stat().st_size / 1024
if size_kb > 100:
    sys.exit(f"Error: submission.zip size ({size_kb:.1f} KB) exceeds 100 KB ceiling.")

print(f"\n[OK] submission.zip created and verified: {size_kb:.2f} KB (< 100 KB ceiling).")
print(f"[OK] Clean production single-agent package with {len(PRODUCTION_FILES)} files ready for leaderboard submission.")
