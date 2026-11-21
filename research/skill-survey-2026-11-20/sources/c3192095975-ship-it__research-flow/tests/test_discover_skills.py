from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "discover_skills.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class DiscoverSkillsTests(unittest.TestCase):
    def run_catalog(self, args: list[str], env: dict[str, str] | None = None) -> dict:
        merged_env = os.environ.copy()
        merged_env["PYTHONDONTWRITEBYTECODE"] = "1"
        if env:
            merged_env.update(env)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=True,
            capture_output=True,
            text=True,
            env=merged_env,
        )
        return json.loads(result.stdout)

    def test_discovery_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            search = base / "root_a" / "search"
            write(search / "SKILL.md", "---\nname: search\ndescription: >\n  Literature search across PubMed.\n---\nUse ${MISSING_TEST_KEY}.\n")
            write(search / "agents" / "openai.yaml", 'dependencies:\n  tools:\n    - type: "mcp"\n      value: "academic-search"\n')

            plot = base / "root_b" / "plot"
            write(plot / "SKILL.md", '---\nname: plot\ndescription: "Make publication outputs."\n---\n')
            write(plot / "scripts" / "make_figure.py", "print(1)\n")
            write(plot / "references" / "figure_qa.md", "# Figure QA\n# Matplotlib layout\n")

            manifest = base / "root_c" / "manifest"
            write(manifest / "manifest.yaml", "name: manifest\ndescription: >\n  Statistical reporting and experimental unit audit.\n")

            meta = base / "root_d" / "meta"
            write(meta / "agents" / "openai.yaml", 'interface:\n  display_name: "Meta"\n  short_description: "Presentation slides and docx delivery"\npolicy:\n  allow_implicit_invocation: false\n')

            for root_name in ("root_e", "root_f"):
                reader = base / root_name / "reader"
                write(reader / "SKILL.md", '---\nname: reader\ndescription: "Full-paper reader with page locators."\n---\n')

            overrides = base / "overrides.yaml"
            write(overrides, "roles:\n  search: search\n  figures: plot\n  writing: missing-writer\n")

            cmd = [sys.executable, str(SCRIPT), "--no-default-roots", "--no-auto-overrides"]
            for root_name in ("root_a", "root_b", "root_c", "root_d", "root_e", "root_f"):
                cmd.extend(["--root", str(base / root_name)])
            cmd.extend(["--overrides", str(overrides)])

            env = {"PYTHONDONTWRITEBYTECODE": "1"}
            catalog = self.run_catalog(cmd[2:], env=env)
            by_name = {skill["name"]: skill for skill in catalog["skills"]}

            search_skill = by_name["search"]
            self.assertEqual(search_skill["missing_env_vars"], ["MISSING_TEST_KEY"])
            self.assertEqual(search_skill["availability"], "unavailable")
            self.assertTrue(search_skill["requires_mcp"])
            self.assertIn("search", [item["name"] for item in search_skill["capabilities"]])

            plot_skill = by_name["plot"]
            self.assertTrue(plot_skill["has_scripts"])
            self.assertIn("figures", [item["name"] for item in plot_skill["capabilities"]])

            self.assertEqual(by_name["manifest"]["format"], "manifest_fallback")
            self.assertEqual(by_name["manifest"]["availability"], "unverified")
            self.assertIn("statistics", [item["name"] for item in by_name["manifest"]["capabilities"]])

            self.assertEqual(by_name["meta"]["format"], "metadata_fallback")
            self.assertFalse(by_name["meta"]["implicit_invocation"])
            self.assertIn("delivery", [item["name"] for item in by_name["meta"]["capabilities"]])

            self.assertIn("reader", catalog["duplicate_names"])
            self.assertIsNone(catalog["overrides"]["resolved"]["search"]["selected"])
            self.assertEqual(catalog["overrides"]["resolved"]["figures"]["selected"], "plot")
            self.assertFalse(catalog["overrides"]["resolved"]["writing"]["available"])

    def test_empty_catalog_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "empty"
            empty.mkdir()
            catalog = self.run_catalog(["--no-default-roots", "--root", str(empty)])
            self.assertEqual(catalog["summary"]["unique_skills"], 0)
            self.assertEqual(catalog["summary"]["errors"], 0)
            self.assertTrue((ROOT / "references" / "baseline-protocol.md").is_file())


if __name__ == "__main__":
    unittest.main()
