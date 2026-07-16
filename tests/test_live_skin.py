#!/usr/bin/env python3
"""Static and deterministic checks for the live Codex skin path."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "skills/redesign-codex-ui/scripts/live_skin_macos.py"
INJECTOR = ROOT / "skills/redesign-codex-ui/scripts/live_skin_injector.mjs"
PRESET = ROOT / "skills/redesign-codex-ui/assets/theme-library/presets/keepsake-olive.json"
IDENTITY = ROOT / "skills/redesign-codex-ui/assets/default-identity/opcspace-ip-avatar.png"

spec = importlib.util.spec_from_file_location("live_skin_macos", CONTROLLER)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

assert module.OFFICIAL_BUNDLE_ID == "com.openai.codex"
assert module.OFFICIAL_TEAM_ID
assert module.DEFAULT_PRESET.is_file()
assert module.DEFAULT_IDENTITY.is_file()

node = shutil.which("node")
if node:
    subprocess.run([node, "--check", str(INJECTOR)], check=True)
    result = subprocess.run(
        [node, str(INJECTOR), "check", "--preset", str(PRESET), "--identity", str(IDENTITY)],
        check=True, capture_output=True, text=True,
    )
    report = json.loads(result.stdout)
    assert report["themeId"] == "keepsake-olive"
    assert report["cssBytes"] > 1000
    assert report["identityBytes"] > 1000

source = INJECTOR.read_text(encoding="utf-8")
for safeguard in ('target.title === "Codex"', 'target.url?.startsWith("app://")', "127.0.0.1"):
    assert safeguard in source

print("live skin deterministic tests passed")
