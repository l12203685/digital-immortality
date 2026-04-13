"""Unit tests for kill_window floor logic (SOP#118 L3 Evolve).

Covers:
  - evolve_execution_rules: kill_window tightens by 5 per kill, clamped to floor
  - recover_kill_window: loosens by 5 after clean streak, capped at ceiling
  - KillMonitor: MDD / WR / PF kill triggers + window-size gating
  - Edge cases: exactly at threshold, floor==ceiling, repeated kills
"""
import unittest
from unittest.mock import patch
from trading.engine import (
    DEFAULT_EXECUTION_RULES,
    KillMonitor,
    evolve_execution_rules,
    recover_kill_window,
)


def _rules(**overrides) -> dict:
    """Build execution rules with optional overrides."""
    r = dict(DEFAULT_EXECUTION_RULES)
    r.update(overrides)
    return r


class TestEvolveExecutionRules(unittest.TestCase):
    """Kill tightens kill_window by 5, floored at kill_window_floor."""

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_single_kill_reduces_window(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=50)
        result = evolve_execution_rules("dualma", "PF 0.7", rules)
        self.assertEqual(result["kill_window"], 45)
        self.assertEqual(result["kill_count"], 1)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_multiple_kills_respect_floor(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=50, kill_window_floor=20)
        for i in range(10):
            rules = evolve_execution_rules(f"s{i}", "MDD", rules)
        self.assertEqual(rules["kill_window"], 20)
        self.assertEqual(rules["kill_count"], 10)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_already_at_floor_stays(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=20, kill_window_floor=20)
        result = evolve_execution_rules("x", "WR", rules)
        self.assertEqual(result["kill_window"], 20)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_floor_equals_ceiling(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=30, kill_window_floor=30, kill_window_ceiling=30)
        result = evolve_execution_rules("x", "PF", rules)
        self.assertEqual(result["kill_window"], 30)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_exactly_one_above_floor(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=25, kill_window_floor=20)
        result = evolve_execution_rules("x", "PF", rules)
        self.assertEqual(result["kill_window"], 20)


class TestRecoverKillWindow(unittest.TestCase):
    """Clean streak loosens kill_window by 5, capped at ceiling."""

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_recovery_after_clean_streak(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=30, kill_window_ceiling=50,
                        kill_window_recovery_ticks=100)
        result = recover_kill_window(rules, 100)
        self.assertEqual(result["kill_window"], 35)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_no_recovery_before_threshold(self, mock_path):
        rules = _rules(kill_window=30, kill_window_recovery_ticks=100)
        result = recover_kill_window(rules, 99)
        self.assertEqual(result["kill_window"], 30)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_recovery_capped_at_ceiling(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=48, kill_window_ceiling=50)
        result = recover_kill_window(rules, 200)
        self.assertEqual(result["kill_window"], 50)

    def test_already_at_ceiling_no_change(self):
        rules = _rules(kill_window=50, kill_window_ceiling=50)
        result = recover_kill_window(rules, 200)
        self.assertEqual(result["kill_window"], 50)

    @patch("trading.engine.EXECUTION_RULES_PATH")
    def test_immutability_original_unchanged(self, mock_path):
        mock_path.exists.return_value = False
        rules = _rules(kill_window=30, kill_window_ceiling=50)
        recover_kill_window(rules, 100)
        self.assertEqual(rules["kill_window"], 30)


class TestKillMonitor(unittest.TestCase):
    """KillMonitor triggers: MDD, WR, PF within the evaluation window."""

    def test_no_kill_below_window_size(self):
        km = KillMonitor(window=10)
        for _ in range(9):
            km.record("s1", -5.0)
        self.assertIsNone(km.check("s1"))

    def test_mdd_trigger(self):
        km = KillMonitor(max_dd=10.0, window=5)
        for _ in range(5):
            km.record("s1", -3.0)  # cumulative drawdown = 15%
        result = km.check("s1")
        self.assertIsNotNone(result)
        self.assertIn("MDD", result)

    def test_wr_trigger(self):
        km = KillMonitor(max_dd=99, min_wr=0.30, min_pf=0.0, window=10)
        # 2 wins, 8 losses -> WR = 20%
        for _ in range(2):
            km.record("s1", 1.0)
        for _ in range(8):
            km.record("s1", -0.1)
        result = km.check("s1")
        self.assertIsNotNone(result)
        self.assertIn("WR", result)

    def test_pf_trigger(self):
        km = KillMonitor(max_dd=99, min_wr=0.0, min_pf=0.8, window=10)
        # 5 wins @ 0.3, 5 losses @ -0.5 -> PF = 1.5/2.5 = 0.6
        for _ in range(5):
            km.record("s1", 0.3)
        for _ in range(5):
            km.record("s1", -0.5)
        result = km.check("s1")
        self.assertIsNotNone(result)
        self.assertIn("PF", result)

    def test_no_kill_when_healthy(self):
        km = KillMonitor(max_dd=20, min_wr=0.30, min_pf=0.8, window=10)
        # 7 wins @ 1.0, 3 losses @ -0.5 -> WR=70%, PF=7/1.5=4.67, MDD small
        for _ in range(7):
            km.record("s1", 1.0)
        for _ in range(3):
            km.record("s1", -0.5)
        self.assertIsNone(km.check("s1"))

    def test_exactly_at_mdd_threshold(self):
        km = KillMonitor(max_dd=10.0, min_wr=0.0, min_pf=0.0, window=2)
        km.record("s1", 0.0)
        km.record("s1", -10.0)  # MDD exactly 10.0 = threshold, not exceeded
        self.assertIsNone(km.check("s1"))


if __name__ == "__main__":
    unittest.main()
