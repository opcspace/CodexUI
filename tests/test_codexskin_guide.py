import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = REPO_ROOT / "docs" / "codex-cdp-skin-launcher.md"


class CodexSkinGuideContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE_PATH.read_text(encoding="utf-8")

    def test_guide_covers_the_complete_portable_skin_workflow(self):
        required_copy = (
            "制作、导入与导出指南",
            "### 4.4 导出已安装皮肤",
            "### 4.5 导出后回导与校验",
            "⇧⌘E",
            "shasum -a 256",
            "切换到此皮肤",
            "重新应用",
            "重试切换",
        )
        for text in required_copy:
            with self.subTest(text=text):
                self.assertIn(text, self.guide)

    def test_preview_is_a_final_standalone_composite(self):
        self.assertRegex(self.guide, r"(?m)^├── preview\.png\s")
        self.assertIn("16:10", self.guide)
        self.assertIn("不能只用背景图", self.guide)

        skin_examples = []
        for block in re.findall(r"```json\s*(.*?)```", self.guide, re.DOTALL):
            decoded = json.loads(block)
            if isinstance(decoded, dict) and "schemaVersion" in decoded:
                skin_examples.append(decoded)

        self.assertTrue(skin_examples, "指南必须包含可解析的 skin.json 示例")
        for example in skin_examples:
            with self.subTest(skin_id=example.get("id")):
                self.assertEqual(example.get("preview"), "preview.png")

    def test_import_and_export_entry_points_match_the_manager(self):
        for text in ("双击", "⌘O", "拖入", "工具栏", "导入", "导出"):
            with self.subTest(text=text):
                self.assertIn(text, self.guide)

        self.assertIn("redistributionAllowed", self.guide)
        self.assertRegex(self.guide, r"仅限本机.{0,80}(锁定|不可导出)")
        self.assertIn("回导", self.guide)

    def test_runtime_port_is_not_part_of_a_skin_package(self):
        self.assertIn("127.0.0.1:9340", self.guide)
        self.assertIn("皮肤包不配置端口", self.guide)
        self.assertIn("不是官方 Codex 的固定接口", self.guide)

    def test_lower_left_account_control_is_a_reserved_safe_area(self):
        self.assertIn("-2 / -1 / 0", self.guide)
        self.assertIn("0px", self.guide)
        self.assertRegex(self.guide, r"左下角.{0,40}账号.{0,40}安全区")

    def test_relative_markdown_links_resolve(self):
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", self.guide)
        relative_links = [
            link
            for link in links
            if not re.match(r"^(?:https?://|mailto:|#)", link)
        ]
        self.assertTrue(relative_links, "指南至少应链接到转换 Skill")

        for link in relative_links:
            target = link.split("#", 1)[0]
            with self.subTest(link=link):
                self.assertTrue(
                    (GUIDE_PATH.parent / target).resolve().exists(),
                    f"失效的相对链接：{link}",
                )


if __name__ == "__main__":
    unittest.main()
