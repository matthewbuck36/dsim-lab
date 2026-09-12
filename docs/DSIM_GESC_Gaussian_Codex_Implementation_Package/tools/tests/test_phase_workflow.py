"""Exercise the actual phase tools in disposable repositories, without ROS."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PACKAGE_REL = Path("docs/DSIM_GESC_Gaussian_Codex_Implementation_Package")
DOCS_REL = Path("docs/codex/gesc_gaussian")
SOURCE_PACKAGE = Path(__file__).resolve().parents[2]
TOOLS = (
    "validate_phase_context.sh",
    "init_phase_status.sh",
    "checkpoint_phase.sh",
)
HEADINGS = (
    "## Verified repository state",
    "## Current milestone",
    "## Validation checkpoints",
    "## Attempts not to repeat",
    "## Remaining work",
    "## Compaction recovery",
)


class PhaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="phase tools ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / PACKAGE_REL
        self.docs = self.root / DOCS_REL
        for tool in TOOLS:
            target = self.package / "tools" / tool
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_PACKAGE / "tools" / tool, target)
        self.write("AGENTS.md", "fixture instructions\n")
        for name in (
            "START_HERE.md",
            "00_MASTER_IMPLEMENTATION_PLAN.md",
            "01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md",
            "07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md",
        ):
            self.write(PACKAGE_REL / name, "fixture context\n")
        self.write(
            PACKAGE_REL / "templates/codex_phase_status.md",
            (SOURCE_PACKAGE / "templates/codex_phase_status.md").read_text(),
        )
        for name in ("README.md", "environment_parameters.md"):
            self.write(Path("docs") / name, "fixture navigation\n")
        for name in (
            "implementation_sequence.md", "repo_audit.md", "repo_map.md",
            "interface_map.md", "test_commands.md",
            "knowledge_bridge_phase_00_05.md",
            "validation/phase_08_final_report.md",
            "validation/phase_08_8_final_report.md",
            "validation/phase_08_v3_gate_results.json",
            "status/phase_08_status.md",
            "checkpoints/phase_08_checkpoint.txt",
            "plans/phase_08_7_plan.md",
            "plans/phase_08_8_plan.md",
        ):
            self.write(DOCS_REL / name, "fixture retained evidence\n")
        for phase in [f"{i:02d}" for i in range(11)] + [
            "05_5", "07_5", "08_1", "08_2", "08_3", "08_8"
        ]:
            self.write(DOCS_REL / f"handoffs/phase_{phase}_handoff.md", "handoff\n")
        self.git("init", "-q")
        self.git("config", "user.name", "Workflow Test")
        self.git("config", "user.email", "workflow-test@example.invalid")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture baseline")

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return target

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments], cwd=self.root, check=True,
            capture_output=True, text=True, timeout=10,
        ).stdout

    def tool(self, name, *arguments, code=0, env=None):
        result = subprocess.run(
            [str(self.package / "tools" / name), *arguments],
            cwd=self.root, capture_output=True, text=True, timeout=10, env=env,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def prepare_v2(self):
        self.write(DOCS_REL / "v2/plan.md", "# Approved V2 plan\n")
        self.tool("init_phase_status.sh", "v2")

    def checkpoint(self):
        self.tool("checkpoint_phase.sh", "v2")
        checkpoint = (self.docs / "v2/checkpoint.txt").read_text()
        self.assertEqual(list((self.docs / "v2").glob(".checkpoint.*")), [])
        self.assertNotIn(".checkpoint.", checkpoint)
        return checkpoint

    @staticmethod
    def field(checkpoint, label):
        prefix = label + ": "
        return next(line[len(prefix):] for line in checkpoint.splitlines()
                    if line.startswith(prefix))

    def test_numeric_plan_context_is_preserved_for_all_phases(self):
        for phase in range(11):
            with self.subTest(phase=phase):
                result = self.tool(
                    "validate_phase_context.sh", str(phase), "plan", "--strict-history"
                )
                self.assertIn(f"Phase {phase:02d} plan context is complete", result.stdout)

    def test_numeric_implementation_and_checkpoint_keep_existing_paths(self):
        for phase in ("00", "08", "09", "10"):
            with self.subTest(phase=phase):
                self.write(DOCS_REL / f"plans/phase_{phase}_plan.md", "saved plan\n")
                status = self.docs / f"status/phase_{phase}_status.md"
                if status.exists():
                    status.unlink()
                self.tool("init_phase_status.sh", phase)
                result = self.tool("validate_phase_context.sh", phase, "implement")
                self.assertIn(f"Phase {phase} implement context is complete", result.stdout)
                if phase == "08":
                    self.assertIn("phase_08_8_plan.md", result.stdout)
                self.tool("checkpoint_phase.sh", phase)
                checkpoint = (self.docs / f"checkpoints/phase_{phase}_checkpoint.txt").read_text()
                self.assertIn(f"# Phase {phase} checkpoint", checkpoint)
                self.assertIn("Unstaged diff sha256:", checkpoint)
        self.assertFalse((self.docs / "v2").exists())

    def test_v2_plan_and_implementation_require_their_own_context(self):
        missing = self.tool("validate_phase_context.sh", "v2", "plan", code=1)
        self.assertIn("v2/plan.md", missing.stderr)
        self.write(DOCS_REL / "v2/plan.md", "# Approved V2 plan\n")
        self.tool("validate_phase_context.sh", "v2", "plan", "--strict-history")
        missing = self.tool("validate_phase_context.sh", "v2", "implement", code=1)
        self.assertIn("v2/status.md", missing.stderr)
        self.tool("init_phase_status.sh", "v2")
        status = self.docs / "v2/status.md"
        self.assertIn("# GESC Gaussian V2 Live Status", status.read_text())
        self.assertIn("docs/codex/gesc_gaussian/v2/plan.md", status.read_text())
        self.assertNotIn("phase_XX", status.read_text())
        self.tool("validate_phase_context.sh", "v2", "implement")
        status.write_text(status.read_text().replace(HEADINGS[-1], "## Renamed section"))
        missing = self.tool("validate_phase_context.sh", "v2", "implement", code=1)
        self.assertIn(HEADINGS[-1], missing.stderr)

    def test_initializer_preserves_nonempty_and_refuses_empty_existing_status(self):
        for phase, relative in (
            ("v2", "v2/status.md"), ("00", "status/phase_00_status.md")
        ):
            with self.subTest(phase=phase):
                status = self.write(DOCS_REL / relative, "operator-owned evidence\n")
                self.tool("init_phase_status.sh", phase)
                self.assertEqual(status.read_text(), "operator-owned evidence\n")
                status.write_text("")
                self.tool("init_phase_status.sh", phase, code=1)
                self.assertEqual(status.read_text(), "")

    def test_v2_context_still_requires_baseline_documents_and_executable_tools(self):
        self.prepare_v2()
        baseline = self.root / "docs/environment_parameters.md"
        baseline.unlink()
        missing = self.tool("validate_phase_context.sh", "v2", "plan", code=1)
        self.assertIn(str(baseline), missing.stderr)
        baseline.write_text("restored\n")
        checkpoint_tool = self.package / "tools/checkpoint_phase.sh"
        checkpoint_tool.chmod(0o644)
        missing = self.tool("validate_phase_context.sh", "v2", "plan", code=1)
        self.assertIn("not executable", missing.stderr)

    def test_v2_checkpoint_requires_plan_and_status_before_writing(self):
        self.tool("checkpoint_phase.sh", "v2", code=1)
        self.tool("init_phase_status.sh", "v2")
        self.tool("checkpoint_phase.sh", "v2", code=1)
        self.assertFalse((self.docs / "v2/checkpoint.txt").exists())

    def test_v2_checkpoint_hashes_binary_staged_untracked_deleted_and_symlink_files(self):
        self.prepare_v2()
        old_checkpoint = (self.docs / "checkpoints/phase_08_checkpoint.txt").read_bytes()
        tracked = self.root / "tracked binary.bin"
        tracked.write_bytes(b"baseline\0")
        deleted = self.write("deleted.txt", "old data\n")
        self.git("add", "tracked binary.bin", "deleted.txt")
        self.git("commit", "-qm", "tracked test files")
        tracked.write_bytes(b"staged\0")
        self.git("add", "tracked binary.bin")
        tracked.write_bytes(b"working\0")
        deleted.unlink()
        unusual_name = "untracked $name\nwith spaces.bin"
        untracked = self.root / unusual_name
        untracked.write_bytes(b"first\0")
        (self.root / "external link").symlink_to("/a/target/never/read")
        self.write(".gitignore", "ignored.bin\n")
        (self.root / "ignored.bin").write_bytes(b"ignored")
        first = self.checkpoint()
        entries = {
            row["path"]: row for row in (
                json.loads(line) for line in first.splitlines() if line.startswith('{"')
            )
        }
        self.assertEqual(entries["tracked binary.bin"]["sha256"], hashlib.sha256(b"working\0").hexdigest())
        self.assertEqual(entries[unusual_name]["sha256"], hashlib.sha256(b"first\0").hexdigest())
        self.assertEqual(entries["external link"]["type"], "symlink")
        self.assertEqual(entries["external link"]["sha256"], hashlib.sha256(os.fsencode("/a/target/never/read")).hexdigest())
        self.assertEqual(entries["deleted.txt"]["type"], "deleted")
        self.assertNotIn("ignored.bin", entries)
        self.assertNotIn(str(DOCS_REL / "v2/checkpoint.txt"), entries)
        self.assertIn(str(DOCS_REL / "v2/plan.md"), entries)
        self.assertIn(str(DOCS_REL / "v2/status.md"), entries)
        untracked.write_bytes(b"second\0")
        second = self.checkpoint()
        self.assertNotEqual(self.field(first, "Dirty and untracked manifest sha256"), self.field(second, "Dirty and untracked manifest sha256"))
        for label in ("Unstaged binary diff sha256", "Staged binary diff sha256"):
            self.assertEqual(self.field(first, label), self.field(second, label))
        tracked.write_bytes(b"changed binary\0")
        third = self.checkpoint()
        self.assertNotEqual(self.field(second, "Unstaged binary diff sha256"), self.field(third, "Unstaged binary diff sha256"))
        self.assertEqual(self.field(second, "Staged binary diff sha256"), self.field(third, "Staged binary diff sha256"))
        self.git("add", "tracked binary.bin")
        fourth = self.checkpoint()
        self.assertNotEqual(self.field(third, "Staged binary diff sha256"), self.field(fourth, "Staged binary diff sha256"))
        self.assertEqual(old_checkpoint, (self.docs / "checkpoints/phase_08_checkpoint.txt").read_bytes())

    def test_v2_checkpoint_captures_latest_milestone(self):
        self.prepare_v2()
        status = self.docs / "v2/status.md"
        status.write_text(status.read_text() + "\n## Current milestone\n\nM1 latest\n\n## Remaining work\nNext\n")
        checkpoint = self.checkpoint()
        snapshot = checkpoint.split("## Current milestone snapshot", 1)[1]
        self.assertIn("M1 latest", snapshot)
        self.assertNotIn("Implementation complete: `yes | no`", snapshot)

    def test_v2_checkpoint_hash_failure_preserves_previous_snapshot_and_cleans_temp(self):
        self.prepare_v2()
        previous = self.checkpoint()
        failing_python = self.write("test_bin/python3", "#!/bin/sh\nexit 17\n")
        failing_python.chmod(0o755)
        environment = dict(os.environ, PATH=f"{failing_python.parent}:{os.environ['PATH']}")
        self.tool("checkpoint_phase.sh", "v2", code=17, env=environment)
        self.assertEqual((self.docs / "v2/checkpoint.txt").read_text(), previous)
        self.assertEqual(list((self.docs / "v2").glob(".checkpoint.*")), [])

    def test_invalid_tokens_are_rejected_without_writes(self):
        for token in ("11", "V2", "../v2", "v2;echo"):
            for tool in TOOLS:
                with self.subTest(token=token, tool=tool):
                    args = (token, "plan") if tool == TOOLS[0] else (token,)
                    self.tool(tool, *args, code=2)
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
