# tools/

Utility scripts for the Digital Immortality project.

---

## decision_audit.py — Life Decision Frequency Auditor

Implements **MD-322**: 生活系統=最小決策頻率設計；反覆做同一決策=系統設計失敗
> Life systems = minimum decision frequency design. Repeating the same decision = system design failure.

**Threshold rule**: any decision made >3 times is a system failure and must be automated or defaulted.
**Branch 8.4 priority**: audit 1-week recurring decisions → automate top 3.

**State file**: `memory/decision_audit.json` (persistent across sessions)

### Commands

```bash
# Log a decision occurrence
python tools/decision_audit.py log "what to eat for lunch" --domain food

# Frequency analysis — lists all decisions by count, flags >3 as SYSTEM_FAILURE
python tools/decision_audit.py audit

# Automation suggestions for all SYSTEM_FAILURE decisions (sorted by frequency)
python tools/decision_audit.py suggest

# Pre-populate with a realistic sample week of decisions (seed data)
python tools/decision_audit.py seed
```

### Domains

| Domain     | Label                   |
|------------|-------------------------|
| `food`     | Food / Nutrition        |
| `finance`  | Finance / Money         |
| `health`   | Health / Body           |
| `schedule` | Schedule / Time         |
| `work`     | Work / Productivity     |
| `social`   | Social / Relationships  |

### Status flags in `audit` output

| Flag | Meaning |
|------|---------|
| `✅ OK` | 1–2 occurrences — normal |
| `🟡 AT THRESHOLD` | 3 occurrences — pre-commit a default now |
| `🔴 SYSTEM_FAILURE` | >3 occurrences — automate or default immediately |

---

## generate_market_data.py

Generates synthetic market data for backtesting the trading system.
See `trading/` for usage context.
