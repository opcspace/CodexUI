#!/usr/bin/env python3
"""Verify that source installation changes real files and can roll back."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "redesign-codex-ui"
INSTALLER = SKILL / "scripts" / "apply_theme_to_source.py"
PRESET = SKILL / "assets" / "theme-library" / "presets" / "keepsake-olive.json"
IDENTITY = SKILL / "assets" / "default-identity" / "opcspace-ip-avatar.png"
FIXTURE = ROOT / "tests" / "fixtures" / "local-codex-source"


def run(*args: str) -> None:
    subprocess.run(["python3", str(INSTALLER), *args], check=True, text=True, capture_output=True)


with tempfile.TemporaryDirectory(prefix="codex-ui-source-") as directory:
    target = Path(directory) / "codex"
    shutil.copytree(FIXTURE, target)
    original = (target / "index.html").read_bytes()
    run("--target", str(target), "--preset", str(PRESET), "--identity", str(IDENTITY))
    html = (target / "index.html").read_text(encoding="utf-8")
    css = (target / "styles" / "codex-skin.css").read_text(encoding="utf-8")
    state = json.loads((target / ".codex-skin" / "applied.json").read_text(encoding="utf-8"))
    assert 'data-codex-skin="keepsake-olive"' in html
    assert "data-codex-skin-stylesheet" in html
    assert 'src="assets/codex-skin/identity.png"' in html
    assert "--codex-skin-accent: #8F9B5A" in css
    assert (target / "assets" / "codex-skin" / "identity.png").read_bytes() == IDENTITY.read_bytes()
    assert state["themeId"] == "keepsake-olive"
    run("--target", str(target), "--restore")
    assert (target / "index.html").read_bytes() == original
    assert not (target / "styles" / "codex-skin.css").exists()
    assert not (target / "assets" / "codex-skin" / "identity.png").exists()

print("Source installer apply/restore test passed")
