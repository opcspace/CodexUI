#!/usr/bin/env python3
"""Unit checks for deterministic macOS sidecar transformations."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/redesign-codex-ui/scripts/build_macos_sidecar.py"
spec = importlib.util.spec_from_file_location("build_macos_sidecar", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


with tempfile.TemporaryDirectory(prefix="sidecar-unit-") as directory:
    root = Path(directory)
    preset_path = root / "preset.json"
    preset = {
        "id": "unit-theme",
        "palette": {
            "canvas": "#111111", "surface": "#222222", "surfaceRaised": "#333333",
            "ink": "#EEEEEE", "mutedInk": "#AAAAAA", "accent": "#8844FF",
            "accentSoft": "#DDCCFF", "line": "#555555", "focus": "#6633CC",
        },
    }
    preset_path.write_text(json.dumps(preset), encoding="utf-8")
    loaded = module.load_preset(preset_path)
    assert loaded["id"] == "unit-theme"
    assert module.identity_asset_name(Path("portrait.webp")) == "opcspace-ip-avatar.webp"
    css = module.css_for(loaded, "opcspace-ip-avatar.webp")
    assert 'data-theme-id="unit-theme"' in css
    assert "--color-token-bg-primary: #111111" in css
    assert './assets/opcspace-ip-avatar.webp' in css
    assert module.app_is_running(Path("/definitely/not/a/real/Codex.app")) is False

    info = {
        "CFBundleIdentifier": "com.openai.codex",
        "CFBundleURLTypes": [{"CFBundleURLName": "Codex", "CFBundleURLSchemes": ["codex"]}],
        "ElectronAsarIntegrity": {"Resources/app.asar": {"algorithm": "SHA256", "hash": "old"}},
    }
    updated = module.update_info(info, "space.opc.codexui", "OPCspace Codex", "new-hash")
    assert updated["CFBundleIdentifier"] == "space.opc.codexui"
    assert updated["CFBundleURLTypes"][0]["CFBundleURLSchemes"] == ["opcspace-codex"]
    assert updated["ElectronAsarIntegrity"]["Resources/app.asar"]["hash"] == "new-hash"

    invalid = root / "invalid.json"
    invalid.write_text('{"id":"broken","palette":{}}', encoding="utf-8")
    try:
        module.load_preset(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid preset was accepted")

print("macOS sidecar transformation tests passed")
