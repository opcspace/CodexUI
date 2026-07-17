#!/usr/bin/env python3
"""Contract tests for the read-only legacy skin inspector."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = ROOT / "skills/convert-to-codexskin/scripts/inspect_legacy_skin.py"


class LegacySkinInspectorTests(unittest.TestCase):
    def run_inspector(self, source: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(INSPECTOR), "--source", str(source)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_inventories_directory_without_executing_active_content(self) -> None:
        with tempfile.TemporaryDirectory(prefix="legacy-skin-directory-") as temporary:
            source = Path(temporary) / "my-skin"
            source.mkdir()
            marker = Path(temporary) / "must-not-exist"
            (source / "theme.css").write_text(":root { color: red; }\n", encoding="utf-8")
            (source / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
            (source / "preview.webp").write_bytes(b"RIFFfixtureWEBP")
            (source / "LICENSE.txt").write_text("Private local preview.\n", encoding="utf-8")
            (source / "launch.command").write_text(
                f"#!/bin/zsh\n/usr/bin/touch {marker}\n", encoding="utf-8"
            )
            (source / "injector.js").write_text("throw new Error('never run');\n", encoding="utf-8")

            result = self.run_inspector(source)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())
            report = json.loads(result.stdout)
            self.assertEqual(report["schemaVersion"], 1)
            self.assertEqual(report["inputKind"], "directory")
            categories = {item["path"]: item["category"] for item in report["files"]}
            self.assertEqual(categories["theme.css"], "stylesheet")
            self.assertEqual(categories["hero.png"], "raster-image")
            self.assertEqual(categories["preview.webp"], "image-conversion-required")
            self.assertEqual(categories["LICENSE.txt"], "license")
            self.assertEqual(categories["launch.command"], "active-content")
            self.assertEqual(categories["injector.js"], "active-content")
            self.assertEqual(report["summary"]["activeContent"], 2)
            self.assertTrue(report["conversionPlan"]["requiresTemplateReview"])
            self.assertTrue(report["conversionPlan"]["requiresAssetConversion"])
            self.assertFalse(report["conversionPlan"]["requiresRightsConfirmation"])
            self.assertIn("never execute", report["safety"]["activeContentPolicy"].lower())

    def test_inventories_safe_zip_without_extracting_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="legacy-skin-zip-") as temporary:
            root = Path(temporary)
            source = root / "theme.zip"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("legacy/theme.json", '{"accent":"#FF0000"}')
                archive.writestr("legacy/background.jpg", b"\xff\xd8fixture\xff\xd9")
                archive.writestr("legacy/NOTICE.md", "Original test asset.")

            result = self.run_inspector(source)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["inputKind"], "zip")
            self.assertEqual(
                {item["path"] for item in report["files"]},
                {"legacy/NOTICE.md", "legacy/background.jpg", "legacy/theme.json"},
            )
            self.assertEqual(report["summary"]["files"], 3)
            self.assertEqual(report["summary"]["activeContent"], 0)
            self.assertFalse((root / "legacy").exists())

    def test_rejects_unsafe_zip_paths_and_source_symlinks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="legacy-skin-unsafe-") as temporary:
            root = Path(temporary)
            unsafe_zip = root / "unsafe.zip"
            with zipfile.ZipFile(unsafe_zip, "w") as archive:
                archive.writestr("../escape.css", "body {}")

            zip_result = self.run_inspector(unsafe_zip)
            self.assertNotEqual(zip_result.returncode, 0)
            self.assertIn("不安全", zip_result.stderr)

            real_source = root / "real"
            real_source.mkdir()
            symlink_source = root / "linked"
            symlink_source.symlink_to(real_source, target_is_directory=True)
            symlink_result = self.run_inspector(symlink_source)
            self.assertNotEqual(symlink_result.returncode, 0)
            self.assertIn("符号链接", symlink_result.stderr)


if __name__ == "__main__":
    unittest.main()
