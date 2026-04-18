#!/usr/bin/env python3
"""
Final batch digestion of remaining pla_md files.
Reads each .md file, extracts structured knowledge, appends to JSONL.
"""

import json
import re
import os
from datetime import datetime, timezone, timedelta

REMAINING_FILE = "C:/Users/admin/workspace/digital-immortality/scripts/remaining.txt"
JSONL_PATH = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
TRACKING_PATH = "C:/Users/admin/workspace/digital-immortality/results/digested_set.txt"
TZ = timezone(timedelta(hours=8))

def extract_strategy_name(content, filepath):
    """Extract strategy name from markdown heading or filename."""
    m = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return os.path.splitext(os.path.basename(filepath))[0]

def extract_field(content, field_name):
    """Extract a field value like **Field:** value."""
    m = re.search(rf'\*\*{re.escape(field_name)}:\*\*\s*(.+)', content)
    if m:
        return m.group(1).strip()
    return None

def extract_parameters(content):
    """Extract parameter table entries."""
    params = []
    in_params = False
    for line in content.split('\n'):
        if '| Name |' in line and 'Type' in line:
            in_params = True
            continue
        if in_params:
            if line.strip().startswith('|---'):
                continue
            if not line.strip().startswith('|'):
                in_params = False
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2 and parts[0]:
                params.append(parts[0])
    return params

def extract_variables(content):
    """Extract variable names."""
    variables = []
    in_vars = False
    for line in content.split('\n'):
        if '| Name |' in line and 'Default' in line and 'Type' not in line:
            in_vars = True
            continue
        if in_vars:
            if line.strip().startswith('|---'):
                continue
            if not line.strip().startswith('|'):
                in_vars = False
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 1 and parts[0]:
                variables.append(parts[0])
    return variables

def extract_code_blocks(content):
    """Extract easylanguage code blocks."""
    blocks = re.findall(r'```easylanguage\n(.*?)```', content, re.DOTALL)
    return '\n'.join(blocks)

def detect_indicators(code):
    """Detect indicators used in code."""
    indicators = set()
    indicator_patterns = {
        'RSI': r'\bRSI\b',
        'MACD': r'\bMACD\b',
        'Bollinger': r'\bBollinger|BBand\b',
        'Average/MA': r'\baverage\s*\(|MovAvg|XAverage\b',
        'Stochastic': r'\bStochastic|FastK|SlowK\b',
        'ADX': r'\bADX\b',
        'ATR': r'\bATR|AvgTrueRange|TrueRange\b',
        'Aroon': r'\baroon\b',
        'CCI': r'\bCCI\b',
        'KD': r'\bKD\b',
        'Highest/Lowest': r'\bHighest\b|\bLowest\b',
        'Volume': r'\bVolume\b|\bTicks\b',
        'DMI': r'\bDMI|PlusDM|MinusDM\b',
        'Momentum': r'\bMomentum\b',
        'SAR': r'\bSar\b|\bParabolicSAR\b',
        'WilliamsR': r'\bWilliamsR\b',
        'OBV': r'\bOBV\b',
        'Pivot': r'\bPivot\b',
        'VWAP': r'\bVWAP\b',
    }
    for name, pattern in indicator_patterns.items():
        if re.search(pattern, code, re.IGNORECASE):
            indicators.add(name)
    return sorted(indicators)

def detect_direction(code, content):
    """Detect trading direction."""
    has_buy = bool(re.search(r'\bbuy\b|\bLE\b', code, re.IGNORECASE))
    has_sell = bool(re.search(r'\bsellshort\b|\bSE\b', code, re.IGNORECASE))
    # Check content fields too
    direction_field = extract_field(content, 'Direction')
    if direction_field:
        return direction_field
    if has_buy and has_sell:
        return "Both"
    elif has_buy:
        return "Long only"
    elif has_sell:
        return "Short only"
    return "unknown"

def detect_timeframe(content, code):
    """Detect trading timeframe."""
    tf = extract_field(content, 'Timeframe')
    if tf:
        return tf
    # Check BarRefValue for intraday
    m = re.search(r'BarRefValue.*?(\d+)', content)
    if m:
        val = int(m.group(1))
        if val <= 5:
            return f"{val}-min intraday"
        elif val <= 60:
            return f"{val}-min intraday"
        elif val <= 1440:
            return "daily"
    if 'SetExitOnClose' in code or 'sess1firstbartime' in code:
        return "intraday"
    return "unknown"

def detect_category(code, content, name):
    """Detect strategy category."""
    cat = extract_field(content, 'Classification')
    if cat:
        return cat
    code_lower = code.lower()
    name_lower = name.lower()
    if 'setexitonclose' in code_lower or 'dt' in name_lower or 'daytrad' in name_lower:
        return "Day Trading"
    if 'swing' in name_lower or 'wave' in name_lower:
        return "Swing Trading"
    if 'trend' in code_lower or 'lt' in name_lower:
        return "Trend Following"
    if 'mean' in name_lower or 'reversion' in name_lower or 'mr' in name_lower:
        return "Mean Reversion"
    if 'breakout' in code_lower or 'bo' in name_lower:
        return "Breakout"
    return "Systematic Trading"

def detect_exit_logic(code):
    """Detect exit mechanisms."""
    exits = {}
    if re.search(r'SetStopLoss|stoploss|stop_loss|entryprice\s*[-+]', code, re.IGNORECASE):
        exits['stop_loss'] = True
    if re.search(r'SetProfitTarget|profit_target|PT', code, re.IGNORECASE):
        exits['profit_target'] = True
    if re.search(r'trailing|trail', code, re.IGNORECASE):
        exits['trailing_stop'] = True
    if re.search(r'SetExitOnClose|exitonclose', code, re.IGNORECASE):
        exits['time_exit'] = True
    if re.search(r'\bsell\b.*\bmarket\b|\bbuytocover\b.*\bmarket\b', code, re.IGNORECASE):
        exits['signal_exit'] = True
    return exits

def detect_entry_logic(code):
    """Detect entry mechanisms."""
    entries = []
    if re.search(r'\bbuy\b.*\bstop\b', code, re.IGNORECASE):
        entries.append("stop-order long")
    if re.search(r'\bbuy\b.*\bmarket\b', code, re.IGNORECASE):
        entries.append("market long")
    if re.search(r'\bbuy\b.*\blimit\b', code, re.IGNORECASE):
        entries.append("limit long")
    if re.search(r'\bsellshort\b.*\bstop\b', code, re.IGNORECASE):
        entries.append("stop-order short")
    if re.search(r'\bsellshort\b.*\bmarket\b', code, re.IGNORECASE):
        entries.append("market short")
    if re.search(r'\bsellshort\b.*\blimit\b', code, re.IGNORECASE):
        entries.append("limit short")
    return entries

def detect_helpers(content):
    """Extract helper function names."""
    helpers = re.findall(r'###\s+(f_[^\s(]+|f__[^\s(]+)', content)
    return helpers

def detect_tags(name, code, indicators, category):
    """Generate tags."""
    tags = set()
    name_lower = name.lower()
    # Instrument
    if 'tx' in name_lower:
        tags.add('TX')
    if 'btc' in name_lower or 'bitcoin' in name_lower or 'crypto' in name_lower:
        tags.add('crypto')
    if 'gold' in name_lower or 'gc' in name_lower:
        tags.add('gold')
    if 'es' in name_lower or 'sp500' in name_lower:
        tags.add('ES')
    # Style
    if category == 'Day Trading':
        tags.add('day-trade')
    if category == 'Trend Following':
        tags.add('trend')
    if 'breakout' in name_lower or 'breakout' in code.lower():
        tags.add('breakout')
    if 'gap' in name_lower or 'gap' in code.lower():
        tags.add('gap')
    if 'reversal' in name_lower:
        tags.add('reversal')
    # Add indicator tags
    for ind in indicators:
        tags.add(ind.lower().replace('/', '-'))
    return sorted(tags)

def digest_logic_file(filepath, content):
    """Digest a pre-structured logic file."""
    name = extract_strategy_name(content, filepath)
    classification = extract_field(content, 'Classification') or 'Systematic Trading'
    direction = extract_field(content, 'Direction') or 'unknown'
    timeframe = extract_field(content, 'Timeframe') or 'unknown'

    # Extract entry/exit from structured sections
    entry_lines = []
    exit_lines = []
    in_section = None
    for line in content.split('\n'):
        if '## Entry Logic' in line:
            in_section = 'entry'
            continue
        elif '## Exit Logic' in line:
            in_section = 'exit'
            continue
        elif line.startswith('## '):
            in_section = None
            continue
        if in_section == 'entry' and line.strip().startswith('- '):
            entry_lines.append(line.strip()[2:])
        elif in_section == 'exit' and line.strip().startswith('- '):
            exit_lines.append(line.strip()[2:])

    indicators_section = []
    in_ind = False
    for line in content.split('\n'):
        if '## Indicators' in line:
            in_ind = True
            continue
        elif line.startswith('## '):
            in_ind = False
            continue
        if in_ind and line.strip().startswith('- '):
            indicators_section.append(line.strip()[2:].split(':')[0].strip())

    tags_line = ''
    for line in content.split('\n'):
        if line.startswith('## Tags'):
            continue
        if '## Tags' in content:
            idx = content.index('## Tags')
            rest = content[idx+7:].strip().split('\n')[0]
            tags_line = rest
            break
    tags = [t.strip() for t in tags_line.split(',') if t.strip()] if tags_line else []

    return {
        'source_file': filepath,
        'strategy_name': name,
        'type': 'logic',
        'classification': classification,
        'direction': direction,
        'timeframe': timeframe,
        'entry_logic': entry_lines,
        'exit_logic': exit_lines,
        'indicators': indicators_section,
        'tags': tags,
        'readable': True,
        'timestamp': datetime.now(TZ).isoformat()
    }

def digest_signal_file(filepath, content):
    """Digest a signal/strategy PLA file."""
    name = extract_strategy_name(content, filepath)
    file_type = extract_field(content, 'Type') or 'Strategy'
    modified = extract_field(content, 'Modified') or ''

    params = extract_parameters(content)
    variables = extract_variables(content)
    code = extract_code_blocks(content)
    helpers = detect_helpers(content)

    indicators = detect_indicators(code)
    direction = detect_direction(code, content)
    timeframe = detect_timeframe(content, code)
    category = detect_category(code, content, name)
    exits = detect_exit_logic(code)
    entries = detect_entry_logic(code)
    tags = detect_tags(name, code, indicators, category)

    # Build summary
    summary_parts = [f"{name} — {file_type}"]
    if timeframe != 'unknown':
        summary_parts.append(f"Timeframe: {timeframe}")
    if direction != 'unknown':
        summary_parts.append(f"Direction: {direction}")
    summary_parts.append(f"Category: {category}")
    if indicators:
        summary_parts.append(f"Indicators: {', '.join(indicators)}")
    if entries:
        summary_parts.append(f"Entry: {', '.join(entries)}")
    if exits:
        exit_types = [k.replace('_', ' ') for k in exits.keys()]
        summary_parts.append(f"Exit: {', '.join(exit_types)}")
    if params:
        summary_parts.append(f"Params({len(params)}): {', '.join(params[:5])}")
    if helpers:
        summary_parts.append(f"Helpers: {', '.join(helpers)}")

    summary = '. '.join(summary_parts)

    has_code = len(code) > 10

    return {
        'source_file': filepath,
        'strategy_name': name,
        'type': file_type.lower(),
        'classification': category,
        'direction': direction,
        'timeframe': timeframe,
        'entry_logic': entries,
        'exit_logic': exits,
        'indicators': indicators,
        'parameters': params[:10],  # cap at 10
        'helpers': helpers,
        'tags': tags,
        'summary': summary,
        'has_code': has_code,
        'readable': True,
        'timestamp': datetime.now(TZ).isoformat()
    }


def main():
    # Read remaining files
    with open(REMAINING_FILE, 'r', encoding='utf-8') as f:
        remaining = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(remaining)} remaining files...")

    processed = 0
    errors = 0

    # Open JSONL for append and tracking file for append
    with open(JSONL_PATH, 'a', encoding='utf-8') as jsonl_f, \
         open(TRACKING_PATH, 'a', encoding='utf-8') as track_f:

        for filepath in remaining:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                if not content.strip():
                    # Empty file - still track it
                    entry = {
                        'source_file': filepath,
                        'strategy_name': os.path.splitext(os.path.basename(filepath))[0],
                        'type': 'empty',
                        'readable': False,
                        'timestamp': datetime.now(TZ).isoformat()
                    }
                else:
                    # Determine type by path
                    if '/logic/' in filepath:
                        entry = digest_logic_file(filepath, content)
                    else:
                        entry = digest_signal_file(filepath, content)

                jsonl_f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                track_f.write(filepath + '\n')
                processed += 1

            except Exception as e:
                errors += 1
                # Still track it to avoid re-processing
                error_entry = {
                    'source_file': filepath,
                    'error': str(e),
                    'type': 'error',
                    'timestamp': datetime.now(TZ).isoformat()
                }
                jsonl_f.write(json.dumps(error_entry, ensure_ascii=False) + '\n')
                track_f.write(filepath + '\n')
                print(f"  ERROR: {filepath}: {e}")

    print(f"\nDone. Processed: {processed}, Errors: {errors}")

    # Verify final counts
    with open(TRACKING_PATH, 'r', encoding='utf-8') as f:
        total_tracked = sum(1 for line in f if line.strip())

    import subprocess
    result = subprocess.run(['find', 'E:/投資交易/pla_md/', '-type', 'f', '-name', '*.md'],
                          capture_output=True, text=True)
    total_files = len([l for l in result.stdout.strip().split('\n') if l.strip()])

    pla_tracked = 0
    with open(TRACKING_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if 'pla_md' in line:
                pla_tracked += 1

    print(f"\nVerification:")
    print(f"  Total pla_md files: {total_files}")
    print(f"  pla_md tracked in digested_set: {pla_tracked}")
    print(f"  Total tracked (all sources): {total_tracked}")

if __name__ == '__main__':
    main()
