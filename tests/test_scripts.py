"""脚本集成测试：只使用临时 HOME 和项目，不修改真实配置。"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


KIT = Path(__file__).resolve().parents[1]


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        mock_bin = self.root / "bin"
        mock_bin.mkdir()
        pbcopy = mock_bin / "pbcopy"
        pbcopy.write_text("#!/bin/sh\ncat >/dev/null\n")
        pbcopy.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.root), PATH=f"{mock_bin}:{os.environ['PATH']}")

    def run_script(self, name, *args, success=True):
        result = subprocess.run(["bash", str(KIT / "bin" / name), *args],
                                cwd=self.project, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_install_update_backs_up_prompt_and_preserves_global_rules(self):
        self.run_script("duo-install")
        self.assertEqual(list(self.root.rglob("*.duo-backup.*")), [])
        agents = self.root / ".codex/AGENTS.md"
        agents.write_text("个人规范\n" + agents.read_text() + "\n尾部规范\n")
        prompt = self.root / ".codex/prompts/duo.md"
        prompt.write_text("我的旧提示词\n")
        self.run_script("duo-install")
        self.assertEqual(prompt.read_text(), "我的旧提示词\n")
        self.run_script("duo-install", "--update")
        self.assertIn("执行 <编号>", prompt.read_text())
        self.assertTrue(any(p.read_text() == "我的旧提示词\n" for p in prompt.parent.glob("duo.md.duo-backup.*")))
        self.assertTrue(agents.read_text().startswith("个人规范\n"))
        self.assertTrue(agents.read_text().endswith("尾部规范\n"))
        before = agents.read_bytes()
        backups = list(self.root.rglob("*.duo-backup.*"))
        self.run_script("duo-install", "--update")
        self.assertEqual(before, agents.read_bytes())
        self.assertEqual(backups, list(self.root.rglob("*.duo-backup.*")))

    def test_project_update_preserves_custom_sections_and_work_records(self):
        self.run_script("duo-init")
        agents = self.project / "AGENTS.md"
        agents.write_text(agents.read_text().replace("(一两句话描述项目)", "我的项目") + "\n## 自定义规则\n保留我\n")
        plan = self.project / ".work/plan.md"
        plan.write_text("真实计划\n")
        task = self.project / ".work/tasks/001-task.md"
        task.write_text("进行中\n")
        agents.write_text(agents.read_text().replace("/duo 执行", "/duo 旧执行"))
        before = agents.read_bytes()
        self.run_script("duo-init")
        self.assertEqual(before, agents.read_bytes())
        self.run_script("duo-init", "--update")
        self.assertIn("/duo 执行", agents.read_text())
        self.assertIn("我的项目", agents.read_text())
        self.assertIn("## 自定义规则\n保留我", agents.read_text())
        self.assertEqual(plan.read_text(), "真实计划\n")
        self.assertEqual(task.read_text(), "进行中\n")
        self.assertTrue(any(p.read_bytes() == before for p in self.project.glob("AGENTS.md.duo-backup.*")))
        before = agents.read_bytes()
        self.run_script("duo-init", "--update")
        self.assertEqual(before, agents.read_bytes())

    def test_project_update_migrates_legacy_protocol(self):
        agents = self.project / "AGENTS.md"
        agents.write_text("# 项目\n我的命令\n\n## 协作协议(架构师 + 突击手)\n旧的 Cursor 协议\n\n## 其他规范\n保留\n")
        self.run_script("duo-init", "--update")
        content = agents.read_text()
        self.assertNotIn("旧的 Cursor 协议", content)
        self.assertIn("我的命令", content)
        self.assertIn("## 其他规范\n保留", content)
        self.assertIn("/duo 执行", content)

    def test_update_adds_protocol_to_existing_project_rules(self):
        agents = self.project / "AGENTS.md"
        agents.write_text("# 自有规范\n保留所有内容\n")
        self.run_script("duo-init", "--update")
        self.assertTrue(agents.read_text().startswith("# 自有规范\n保留所有内容\n"))
        self.assertIn("/duo 执行", agents.read_text())

    def test_broken_markers_fail_without_modifying_file(self):
        for name, path in [("duo-install", self.root / ".codex/AGENTS.md"),
                           ("duo-init", self.project / "AGENTS.md")]:
            path.parent.mkdir(parents=True, exist_ok=True)
            begin, end = "<!-- DUO-KIT:BEGIN -->\n", "<!-- DUO-KIT:END -->\n"
            for broken in (begin, end, end + begin, begin + end + begin + end):
                with self.subTest(script=name, markers=broken):
                    path.write_text("我的内容\n" + broken)
                    before = path.read_bytes()
                    self.run_script(name, "--update", success=False)
                    self.assertEqual(before, path.read_bytes())

    def test_project_cursor_rules_are_backed_up_and_records_are_preserved(self):
        self.run_script("duo-init")
        cursor = self.project / ".cursor/rules/main.mdc"
        cursor.write_text("自定义 Cursor 规则\n")
        records = [self.project / ".work/notes.md", self.project / ".work/tasks/001-task.md"]
        for path in records:
            path.write_text("用户自己的记录\n")
        self.run_script("duo-init", "--update")
        self.assertEqual(cursor.read_bytes(), (KIT / "template/.cursor/rules/main.mdc").read_bytes())
        backups = list(cursor.parent.glob("main.mdc.duo-backup.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "自定义 Cursor 规则\n")
        for path in records:
            self.assertEqual(path.read_text(), "用户自己的记录\n")

    def test_task_template_update_backs_up_and_skips_identical_content(self):
        self.run_script("duo-init")
        template = self.project / ".work/tasks/000-template.md"
        source = KIT / "template/.work/tasks/000-template.md"
        self.assertEqual(template.read_bytes(), source.read_bytes())
        template.write_text("自定义旧模板\n")
        self.run_script("duo-init")
        self.assertEqual(template.read_text(), "自定义旧模板\n")
        self.assertEqual(list(template.parent.glob("000-template.md.duo-backup.*")), [])
        self.run_script("duo-init", "--update")
        self.assertEqual(template.read_bytes(), source.read_bytes())
        backups = list(template.parent.glob("000-template.md.duo-backup.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "自定义旧模板\n")
        self.run_script("duo-init", "--update")
        self.assertEqual(template.read_bytes(), source.read_bytes())
        self.assertEqual(backups, list(template.parent.glob("000-template.md.duo-backup.*")))

    def test_unknown_options_fail_and_help_has_no_side_effects(self):
        for name in ("duo-install", "duo-init"):
            self.run_script(name, "--typo", success=False)
            self.run_script(name, "--help")
        self.assertFalse((self.root / ".codex").exists())
        self.assertEqual(list(self.project.iterdir()), [])

    def test_init_does_not_copy_finder_metadata(self):
        self.run_script("duo-init")
        self.assertFalse((self.project / ".DS_Store").exists())


if __name__ == "__main__":
    unittest.main()
