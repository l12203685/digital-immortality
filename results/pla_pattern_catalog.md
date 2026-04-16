# PLA Pattern Catalog

Analyzed **366** digested PLA strategies.

## Indicator Frequency

| Indicator | Count | Status |
|-----------|-------|--------|
| MA | 54 | COVERED |
| ATR | 46 | COVERED |
| Keltner | 19 | untapped |
| Gap | 16 | untapped |
| Slope | 15 | untapped |
| Bollinger | 15 | COVERED |
| Donchian | 15 | COVERED |
| RSI | 13 | COVERED |
| CDP | 13 | untapped |
| KD | 9 | untapped |
| MACD | 7 | COVERED |
| SAR | 7 | untapped |
| CCI | 6 | COVERED |
| Pivot | 5 | untapped |
| ORB | 4 | COVERED |
| WilliamsR | 3 | untapped |
| DMI | 2 | COVERED |
| Volume | 2 | untapped |
| StdDev | 2 | untapped |

## Untapped Indicators

Indicators found in PLA corpus but not in the active strategy pool:

- **Keltner**: 19 strategies
- **Gap**: 16 strategies
- **Slope**: 15 strategies
- **CDP**: 13 strategies
- **KD**: 9 strategies
- **SAR**: 7 strategies
- **Pivot**: 5 strategies
- **WilliamsR**: 3 strategies
- **Volume**: 2 strategies
- **StdDev**: 2 strategies

## Top Indicator Pairs

| Pair | Count |
|------|-------|
| ATR + MA | 10 |
| Gap + MA | 6 |
| Bollinger + Keltner | 6 |
| ATR + Keltner | 5 |
| ATR + RSI | 5 |
| ATR + Donchian | 5 |
| CDP + MA | 5 |
| MA + MACD | 4 |
| ATR + Bollinger | 4 |
| Bollinger + MA | 4 |
| Keltner + MA | 4 |
| MA + Slope | 4 |
| ATR + Slope | 3 |
| ATR + MACD | 3 |
| Donchian + Keltner | 3 |
| ATR + Gap | 3 |
| Gap + RSI | 2 |
| MA + RSI | 2 |
| Keltner + MACD | 2 |
| Donchian + MA | 2 |

## Top Indicator Triples

| Triple | Count |
|--------|-------|
| ATR + Keltner + MACD | 2 |
| ATR + Bollinger + MA | 2 |
| ATR + Bollinger + RSI | 2 |
| DMI + Gap + MA | 1 |
| DMI + Gap + MACD | 1 |
| DMI + Gap + RSI | 1 |
| DMI + MA + MACD | 1 |
| DMI + MA + RSI | 1 |
| DMI + MACD + RSI | 1 |
| Gap + MA + MACD | 1 |

## Observed Parameter Ranges

### ATR

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 1 | 54 | 9 | 1, 2, 3, 5, 8, 9, 13, 22 |

### Bollinger

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 1 | 60 | 19 | 1, 3, 4, 19, 48, 50, 60 |
| std_dev | 2 | 2 | 2 | 1 |

### CCI

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 1 | 100 | 100 | 1, 100 |
| threshold | 1 | 1 | 1 | 1 |

### Donchian

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 1 | 46 | 30 | 1, 2, 3, 30, 36, 46 |

### KD

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 9 | 85 | 74 | 9, 20, 74, 85 |

### MA

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 1 | 320 | 27 | 1, 2, 3, 4, 5, 6, 8, 9 |

### RSI

| Parameter | Min | Max | Median | Sample Values |
|-----------|-----|-----|--------|---------------|
| period | 2 | 70 | 14 | 2, 5, 7, 13, 14, 15, 50, 70 |

## Untapped Indicator Pairs

Pairs where at least one indicator is not in the active pool:

- **Gap + MA**: 6 strategies
- **Bollinger + Keltner**: 6 strategies
- **ATR + Keltner**: 5 strategies
- **CDP + MA**: 5 strategies
- **Keltner + MA**: 4 strategies
- **MA + Slope**: 4 strategies
- **ATR + Slope**: 3 strategies
- **Donchian + Keltner**: 3 strategies
- **ATR + Gap**: 3 strategies
- **Gap + RSI**: 2 strategies
- **Keltner + MACD**: 2 strategies
- **KD + MA**: 2 strategies
- **CDP + Pivot**: 2 strategies
- **CDP + KD**: 2 strategies
