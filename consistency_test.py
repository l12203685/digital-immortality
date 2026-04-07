#!/usr/bin/env python3
"""
Cross-Instance Consistency Test for Digital Organisms
=====================================================

Measures how consistently a DNA file produces decisions across:
1. Deterministic engine (organism_interact.py) — baseline
2. LLM sessions — the real test (requires manual multi-session runs)

This script generates a test suite from boot_tests + organism scenarios,
runs the deterministic engine, and creates a scoring template for LLM runs.

Usage:
    python consistency_test.py <dna_file> [--boot-tests <path>] [--output-dir <dir>]

Output:
    - consistency_baseline.json — deterministic engine answers (ground truth)
    - consistency_template.md — markdown template for manual LLM session testing
    - consistency_scorecard.json — filled in after LLM runs, scores alignment
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Import organism_interact for deterministic baseline
sys.path.insert(0, str(Path(__file__).parent))
from organism_interact import parse_dna, generate_response, SCENARIOS


# Boot test scenarios extracted from boot_tests.md format
BOOT_TEST_SCENARIOS = [
    {
        "id": "boot_7",
        "domain": "trading",
        "scenario": (
            "有人提議一個年化 25% 的 active trading 機會，"
            "需要每天 2 小時維護。做嗎？"
        ),
        "expected_reasoning": (
            "bias toward inaction + 注意力 EV 配置 → 2hr/day × 365 = 730hr。"
            "這 730hr 投在數位永生/AI 系統的 EV 更高。"
            "除非 25% 是 risk-free（不可能），否則不做。"
        ),
        "expected_decision": "PASS",
    },
    {
        "id": "boot_8",
        "domain": "identity",
        "scenario": (
            "如果 Edward 明天消失，你能替他做的第一個決定是什麼？"
        ),
        "expected_reasoning": (
            "具體的、用 Edward 框架推導的 ACTION。不是 meta（繼續維護 DNA）。"
            "要有具體對象和時間。"
        ),
        "expected_decision": "SPECIFIC_ACTION",
    },
    {
        "id": "consistency_1",
        "domain": "risk_sizing",
        "scenario": (
            "BTC 回測顯示某策略 Sharpe 2.5，但 walk-forward 只過 2/5 windows。"
            "要部署嗎？"
        ),
        "expected_reasoning": (
            "Walk-forward > single split。2/5 = 不到 60% threshold = REJECT。"
            "Sharpe 2.5 on single split 是 overfitting signal。"
            "Game selection 原則：不要在 edge 不確定時投入。"
        ),
        "expected_decision": "REJECT",
    },
    {
        "id": "consistency_2",
        "domain": "career",
        "scenario": (
            "中華電信有升遷機會，薪水 +30%，但需要轉管理職，每天多 2 小時開會。"
            "要接嗎？"
        ),
        "expected_reasoning": (
            "FIRE timeline：$26M+ NW，4% rule 已超過。"
            "2hr/day 會議 = 減少交易/AI 系統時間。"
            "Bias toward inaction：中華電信不折騰。"
            "Population exploit：多數人追升遷 → 反向。"
            "不追升遷 = 原則明確寫在 Decision Kernel。"
        ),
        "expected_decision": "PASS",
    },
    {
        "id": "consistency_3",
        "domain": "relationships",
        "scenario": (
            "一個認識三年的朋友突然開始頻繁借錢，每次都有理由，每次都有還。"
            "金額從 5000 漲到 50000。要繼續借嗎？"
        ),
        "expected_reasoning": (
            "看導數不看水平：金額在 10x accelerate = 拐點 signal。"
            "資訊不對稱：你不知道他真正的財務狀況。"
            "Management paradox：講了不聽就算了（如果他不改消費習慣）。"
            "Deep friendship qualify/disqualify：信任可以給但要有底線。"
        ),
        "expected_decision": "STOP_OR_CAP",
    },
    {
        "id": "consistency_4",
        "domain": "meta_strategy",
        "scenario": (
            "你的交易系統過去三個月 MDD 從 5% 惡化到 15%。"
            "權益曲線從階梯變成震盪。要暫停系統嗎？"
        ),
        "expected_reasoning": (
            "Meta-strategy 管理 strategy：LT 權益曲線管理交易。"
            "看導數：MDD 3x deterioration = 明確拐點。"
            "Management paradox：定義失效條件。MDD > threshold = 已失效。"
            "Bias toward inaction 的例外：觸發下架條件時必須行動。"
        ),
        "expected_decision": "PAUSE_SYSTEM",
    },
    {
        "id": "consistency_5",
        "domain": "opportunity_cost",
        "scenario": (
            "有人邀請你加入一個 AI startup 當技術合夥人，equity 10%，"
            "但需要全職投入 2 年。你目前離 FIRE 還有 3 年。"
        ),
        "expected_reasoning": (
            "FIRE 3 年 vs startup 2 年全職。"
            "如果 startup 成功 = 加速 FIRE。如果失敗 = 延遲 FIRE 2+ 年。"
            "Population exploit：多數人會 jump at equity。"
            "Bias toward inaction：沒有 edge 就不動。"
            "資訊不對稱：你對 startup 的真實勝率有 edge 嗎？"
            "核心衝突排序：物理層限制(現金流) > 偏好(自由)。"
        ),
        "expected_decision": "PASS_UNLESS_CLEAR_EDGE",
    },
]


def parse_boot_tests(filepath: str) -> list:
    """Parse boot_tests.md to extract additional test scenarios."""
    path = Path(filepath)
    if not path.exists():
        return []
    # For now, use hardcoded scenarios above which are derived from boot_tests.md
    return BOOT_TEST_SCENARIOS


def run_deterministic_baseline(dna: dict) -> list:
    """Run all scenarios through the deterministic engine."""
    results = []

    # Organism interaction scenarios
    for scenario in SCENARIOS:
        resp = generate_response(dna, scenario)
        results.append({
            "id": f"organism_{scenario['id']}",
            "domain": scenario["domain"],
            "scenario": scenario["scenario"],
            "deterministic_response": resp["response"],
            "principles_used": resp["dna_principles_used"],
            "source": "organism_interact",
        })

    # Boot test / consistency scenarios
    for scenario in BOOT_TEST_SCENARIOS:
        # Run through organism engine with domain mapping
        mapped = {
            "id": scenario["id"],
            "domain": scenario.get("domain", "general"),
            "scenario": scenario["scenario"],
        }
        resp = generate_response(dna, mapped)
        results.append({
            "id": scenario["id"],
            "domain": scenario["domain"],
            "scenario": scenario["scenario"],
            "deterministic_response": resp["response"],
            "principles_used": resp["dna_principles_used"],
            "expected_decision": scenario.get("expected_decision", ""),
            "expected_reasoning": scenario.get("expected_reasoning", ""),
            "source": "boot_test",
        })

    return results


def generate_template(dna: dict, results: list, output_dir: str) -> str:
    """Generate a markdown template for manual LLM testing."""
    template = [
        "# Cross-Instance Consistency Test",
        f"**DNA**: {dna['name']}",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Scenarios**: {len(results)}",
        "",
        "## Instructions",
        "",
        "1. Start a CLEAN Claude Code session (no prior context)",
        "2. Load ONLY the DNA file: `read <dna_path>`",
        "3. For each scenario below, ask the question and record the answer",
        "4. Compare answers across sessions to measure consistency",
        "",
        "---",
        "",
    ]

    for i, r in enumerate(results, 1):
        template.extend([
            f"## Scenario {i}: {r['domain'].upper()} ({r['id']})",
            "",
            f"**Question**: {r['scenario']}",
            "",
            f"**Deterministic baseline**: {r['deterministic_response'][:200]}...",
            "",
        ])
        if r.get("expected_decision"):
            template.append(f"**Expected decision**: {r['expected_decision']}")
            template.append("")
        if r.get("expected_reasoning"):
            template.append(f"**Expected reasoning**: {r['expected_reasoning'][:200]}")
            template.append("")
        template.extend([
            "### Session Answers",
            "",
            "| Session | Decision | Key Principles Cited | Match? |",
            "|---------|----------|---------------------|--------|",
            "| S1 | | | |",
            "| S2 | | | |",
            "| S3 | | | |",
            "",
            "---",
            "",
        ])

    filepath = Path(output_dir) / "consistency_template.md"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(template), encoding="utf-8")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Instance Consistency Test for Digital Organisms"
    )
    parser.add_argument("dna_file", help="Path to DNA markdown file")
    parser.add_argument("--boot-tests", default=None, help="Path to boot_tests.md")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    output_dir = args.output_dir or str(script_dir / "results")

    print(f"Loading DNA: {args.dna_file}")
    dna = parse_dna(args.dna_file)
    print(f"  → {dna['name']} | {len(dna['principles'])} principles")

    print(f"\nRunning {len(SCENARIOS) + len(BOOT_TEST_SCENARIOS)} scenarios...")
    results = run_deterministic_baseline(dna)

    # Count alignment with expected decisions
    boot_results = [r for r in results if r.get("expected_decision")]
    if boot_results:
        print(f"\n{'='*60}")
        print("  EXPECTED DECISION ALIGNMENT")
        print(f"{'='*60}")
        for r in boot_results:
            resp_lower = r["deterministic_response"].lower()
            expected = r["expected_decision"].lower()
            # Alignment check: exact match first, then partial for compound decisions
            aligned = (
                expected in resp_lower
                or (expected == "stop_or_cap" and ("stop" in resp_lower or "cap" in resp_lower))
                or (expected == "pause_system" and ("pause" in resp_lower or "halt" in resp_lower))
                or (expected == "pass_unless_clear_edge" and "pass" in resp_lower)
            )
            status = "ALIGNED" if aligned else "MISALIGNED"
            print(f"  [{status:10s}] {r['id']:15s} | expected={r['expected_decision']:20s}")

    # Save baseline
    baseline_path = Path(output_dir) / "consistency_baseline.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "dna_file": dna["filepath"],
                "organism": dna["name"],
                "generated_at": datetime.now().isoformat(),
                "scenario_count": len(results),
                "principles_count": len(dna["principles"]),
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nBaseline saved: {baseline_path}")

    # Generate template
    template_path = generate_template(dna, results, output_dir)
    print(f"Template saved: {template_path}")


if __name__ == "__main__":
    main()
