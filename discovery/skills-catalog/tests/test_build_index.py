#!/usr/bin/env python3
"""
Unit tests for build-index.py.

The filename has a hyphen and isn't a valid module name, so it's loaded
dynamically via importlib rather than `import build_index`.

Run with: python -m unittest test_build_index
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def _load_build_index():
    spec = importlib.util.spec_from_file_location("build_index", SCRIPTS_DIR / "build-index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bi = _load_build_index()


def _write_skill_md(tmpdir, content, subdir="my-skill"):
    d = Path(tmpdir) / subdir
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(content)
    return p


class TestParseFrontmatter(unittest.TestCase):
    def test_basic_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, "---\nname: my-skill\ndescription: Does a thing. Use when X.\n---\n\n# Body\n")
            name, desc = bi.parse_frontmatter(str(p))
            self.assertEqual(name, "my-skill")
            self.assertEqual(desc, "Does a thing. Use when X.")

    def test_quoted_values_are_stripped(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, '---\nname: "my-skill"\ndescription: \'Quoted desc\'\n---\n')
            name, desc = bi.parse_frontmatter(str(p))
            self.assertEqual(name, "my-skill")
            self.assertEqual(desc, "Quoted desc")

    def test_folded_block_scalar_description(self):
        content = (
            "---\n"
            "name: my-skill\n"
            "description: >\n"
            "  First line of description\n"
            "  continues here.\n"
            "---\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, content)
            name, desc = bi.parse_frontmatter(str(p))
            self.assertEqual(name, "my-skill")
            self.assertIn("First line of description", desc)
            self.assertIn("continues here.", desc)

    def test_missing_description_falls_back_to_first_body_line(self):
        content = "---\nname: my-skill\n---\n\n# Heading\nActual first content line.\nMore.\n"
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, content)
            _, desc = bi.parse_frontmatter(str(p))
            self.assertEqual(desc, "Actual first content line.")

    def test_no_frontmatter_returns_none_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, "# Just a heading\nSome text.\n")
            name, _ = bi.parse_frontmatter(str(p))
            self.assertIsNone(name)

    def test_missing_file_returns_none_none(self):
        name, desc = bi.parse_frontmatter("/nonexistent/path/SKILL.md")
        self.assertIsNone(name)
        self.assertIsNone(desc)

    def test_description_truncated_to_200_chars(self):
        long_desc = "x" * 300
        content = f"---\nname: my-skill\ndescription: {long_desc}\n---\n"
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_skill_md(tmp, content)
            _, desc = bi.parse_frontmatter(str(p))
            self.assertEqual(len(desc), 200)


class TestDeriveTriggers(unittest.TestCase):
    def test_name_tokens_included(self):
        triggers = bi.derive_triggers("pii-scrub", "")
        self.assertIn("pii", triggers)
        self.assertIn("scrub", triggers)

    def test_stopwords_excluded(self):
        triggers = bi.derive_triggers("the-and-of", "")
        self.assertEqual(triggers, [])

    def test_desc_tokens_capped_at_eight(self):
        triggers = bi.derive_triggers("x", "alpha beta gamma delta epsilon zeta eta theta iota kappa")
        self.assertLessEqual(len(triggers), 8)

    def test_no_duplicate_tokens_between_name_and_desc(self):
        triggers = bi.derive_triggers("scrub", "scrub data classification")
        self.assertEqual(triggers.count("scrub"), 1)


class TestCategorize(unittest.TestCase):
    def test_prefix_match(self):
        self.assertEqual(bi.categorize("it-ops-health", ""), "it-ops")

    def test_keyword_match_in_description(self):
        self.assertEqual(bi.categorize("random-name", "a tool for penetration testing"), "security-privacy")

    def test_fallback_category_when_nothing_matches(self):
        self.assertEqual(bi.categorize("totally-unrelated-name", "no matching keywords here"), "engineering")


class TestFindSkillFiles(unittest.TestCase):
    def test_finds_skill_md_and_treats_it_as_a_leaf(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")
            # a fixture SKILL.md nested under an already-found skill must NOT
            # be yielded — a skill dir is a leaf once its own SKILL.md is found
            nested = skill_dir / "assets" / "sample-skill"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text("---\nname: fixture\n---\n")

            found = list(bi.find_skill_files(tmp))
            self.assertEqual(len(found), 1)
            self.assertTrue(found[0].endswith(os.path.join("my-skill", "SKILL.md")))

    def test_skips_junk_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / "__pycache__" / "fake-skill"
            junk.mkdir(parents=True)
            (junk / "SKILL.md").write_text("---\nname: junk\n---\n")
            found = list(bi.find_skill_files(tmp))
            self.assertEqual(found, [])


class TestPluginIdFromPath(unittest.TestCase):
    def test_extracts_plugin_and_marketplace(self):
        path = os.path.join(
            "home", "user", ".claude", "plugins", "cache",
            "my-marketplace", "my-plugin", "1.0.0", "skills", "x", "SKILL.md",
        )
        self.assertEqual(bi.plugin_id_from_path(path), "my-plugin@my-marketplace")

    def test_no_cache_segment_returns_unknown(self):
        self.assertEqual(bi.plugin_id_from_path("/some/other/path/SKILL.md"), "unknown")


class TestBuildSkillsIntegration(unittest.TestCase):
    """End-to-end: real directory scan + realpath dedup + priority assignment."""

    def test_dedup_by_realpath_and_hot_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            agents_root = Path(tmp) / "agents"
            _write_skill_md(
                agents_root,
                "---\nname: skill-tester\ndescription: Validate skills.\n---\n",
                subdir="skill-tester",
            )
            claude_root = Path(tmp) / "claude-skills"
            # same skill, reachable from a second root via a symlink —
            # os.path.realpath must collapse this to a single record
            claude_root.mkdir(parents=True)
            os.symlink(agents_root / "skill-tester", claude_root / "skill-tester")

            original_roots = bi.SKILL_ROOTS
            try:
                bi.SKILL_ROOTS = [
                    ("agents", str(agents_root), "active"),
                    ("claude", str(claude_root), "active"),
                ]
                skills = bi.build_skills(quiet=True)
            finally:
                bi.SKILL_ROOTS = original_roots

            self.assertEqual(len(skills), 1)
            rec = skills[0]
            self.assertEqual(sorted(rec["sources"]), ["agents", "claude"])
            # cursor-meta category (name prefix "skill-tester") is a HOT_CATEGORIES slug
            self.assertEqual(rec["category"], "cursor-meta")
            self.assertEqual(rec["priority"], "hot")


if __name__ == "__main__":
    unittest.main()
