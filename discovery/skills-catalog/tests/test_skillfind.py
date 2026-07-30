#!/usr/bin/env python3
"""
Unit tests for skillfind.

The file has no extension, so it's loaded dynamically via importlib rather
than `import skillfind`.

Run with: python -m unittest test_skillfind
"""
import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def _load_skillfind():
    # spec_from_file_location can't infer a loader for an extension-less file,
    # so the SourceFileLoader is constructed explicitly.
    loader = importlib.machinery.SourceFileLoader("skillfind_mod", str(SCRIPTS_DIR / "skillfind"))
    spec = importlib.util.spec_from_loader("skillfind_mod", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


sf = _load_skillfind()


def _skill(name, triggers=(), desc="", priority="warm"):
    return {
        "name": name,
        "dir": name,
        "sources": ["claude"],
        "status": "active",
        "category": "engineering",
        "path": f"/fake/{name}/SKILL.md",
        "triggers": list(triggers),
        "desc": desc,
        "priority": priority,
    }


class TestWordHit(unittest.TestCase):
    def test_matches_whole_word(self):
        self.assertTrue(sf.word_hit("down", "shut down now"))

    def test_does_not_match_inside_a_longer_word(self):
        self.assertFalse(sf.word_hit("down", "a markdown file"))

    def test_matches_at_start_of_text(self):
        self.assertTrue(sf.word_hit("scrub", "scrubbing data"))


class TestScore(unittest.TestCase):
    def test_name_match_worth_more_than_desc_match(self):
        name_hit = _skill("pii-scrub", desc="unrelated")
        desc_hit = _skill("unrelated-name", desc="redacts pii from logs")
        self.assertGreater(sf.score(name_hit, ["pii"]), sf.score(desc_hit, ["pii"]))

    def test_no_match_scores_zero_even_with_hot_priority(self):
        s = _skill("something", desc="nothing relevant", priority="hot")
        self.assertEqual(sf.score(s, ["xyzzy"]), 0)

    def test_hot_priority_adds_boost_when_there_is_a_match(self):
        hot = _skill("scrub", priority="hot")
        warm = _skill("scrub", priority="warm")
        self.assertGreater(sf.score(hot, ["scrub"]), sf.score(warm, ["scrub"]))

    def test_trigger_match_counts(self):
        s = _skill("x", triggers=["redact", "secrets"])
        self.assertEqual(sf.score(s, ["redact"]), 3)  # trigger weight (2) + warm priority boost (1)


class TestHintBuilders(unittest.TestCase):
    def test_hint_skill_omits_score_by_default(self):
        s = _skill("pii-scrub")
        hint = sf.hint_skill(s)
        self.assertNotIn("score", hint)
        self.assertEqual(hint["name"], "pii-scrub")

    def test_hint_skill_includes_score_when_given(self):
        s = _skill("pii-scrub")
        hint = sf.hint_skill(s, sc=5)
        self.assertEqual(hint["score"], 5)

    def test_hint_rule_shape(self):
        rule = {"name": "absolute-mode", "path": "/fake/absolute-mode.md", "always_on": True}
        hint = sf.hint_rule(rule, sc=3)
        self.assertEqual(hint, {"name": "absolute-mode", "path": "/fake/absolute-mode.md", "score": 3})


class TestLoadIndexIntegration(unittest.TestCase):
    """Real file-system read path: pre-built index.json/rules-index.json, no rebuild."""

    def test_load_index_reads_prebuilt_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.json"
            rules_path = Path(tmp) / "rules-index.json"
            skills = [_skill("pii-scrub", triggers=["pii", "redact"], desc="Redact secrets from files.")]
            index_path.write_text(json.dumps({
                "meta": {"built_at": 9999999999.0, "counts": {"total": 1}},
                "skills": skills,
            }))
            rules_path.write_text(json.dumps({"meta": {"built_at": 9999999999.0}, "rules": []}))

            original_index, original_rules, original_watch = sf.INDEX_PATH, sf.RULES_INDEX_PATH, sf.WATCH_ROOTS
            try:
                sf.INDEX_PATH = str(index_path)
                sf.RULES_INDEX_PATH = str(rules_path)
                sf.WATCH_ROOTS = []  # no source dirs to watch -> never considered stale
                data, rules_data = sf.load_index()
            finally:
                sf.INDEX_PATH, sf.RULES_INDEX_PATH, sf.WATCH_ROOTS = original_index, original_rules, original_watch

            self.assertEqual(len(data["skills"]), 1)
            self.assertEqual(data["skills"][0]["name"], "pii-scrub")
            self.assertEqual(rules_data["rules"], [])

    def test_end_to_end_search_ranks_expected_top_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.json"
            rules_path = Path(tmp) / "rules-index.json"
            skills = [
                _skill("pii-scrub", triggers=["pii", "redact", "secrets"], desc="Redact secrets from files."),
                _skill("tech-debt-tracker", triggers=["debt"], desc="Scan for tech debt."),
            ]
            index_path.write_text(json.dumps({
                "meta": {"built_at": 9999999999.0, "counts": {"total": 2}},
                "skills": skills,
            }))
            rules_path.write_text(json.dumps({"meta": {"built_at": 9999999999.0}, "rules": []}))

            original_index, original_rules, original_watch = sf.INDEX_PATH, sf.RULES_INDEX_PATH, sf.WATCH_ROOTS
            try:
                sf.INDEX_PATH = str(index_path)
                sf.RULES_INDEX_PATH = str(rules_path)
                sf.WATCH_ROOTS = []
                data, _ = sf.load_index()
            finally:
                sf.INDEX_PATH, sf.RULES_INDEX_PATH, sf.WATCH_ROOTS = original_index, original_rules, original_watch

            terms = ["redact", "secrets"]
            scored = sorted(((sf.score(s, terms), s) for s in data["skills"]), key=lambda x: -x[0])
            top_score, top_skill = scored[0]
            self.assertEqual(top_skill["name"], "pii-scrub")
            self.assertGreater(top_score, 0)


if __name__ == "__main__":
    unittest.main()
