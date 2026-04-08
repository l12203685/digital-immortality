# Mainnet Activation Guide — Binance Spot $100

**Status:** Ready to activate. Testnet --review passed (PF=5.839, WR=60%, GO ✓).  
**Strategy:** dual_ma_btc_daily only. SPOT only (LONG=buy BTC, SHORT=sell to USDT, FLAT=hold).  
**Cap:** $100 USDT hard limit. Kill conditions: MDD>10%, PF<0.85, WR<35% (each triggers after ≥5 trades).

---

## Step 1 — Create Binance API Key (5 min)

1. Log in to binance.com → Account → API Management
2. Click "Create API" → label: `digital_immortality_v1`
3. Permissions: **Enable Reading + Enable Spot & Margin Trading**
4. Restrict to IP: add your current IP (Settings → Security for current IP)
5. Copy **API Key** and **Secret Key** — secret shown once only

---

## Step 2 — Store Credentials (2 min)

Option A — JSON file (recommended, no env leak):
```bash
mkdir -p ~/.claude/credentials
cat > ~/.claude/credentials/binance_api.json << 'EOF'
{
  "api_key": "YOUR_API_KEY_HERE",
  "secret_key": "YOUR_SECRET_KEY_HERE"
}
EOF
```

Option B — Environment variables:
```bash
export BINANCE_API_KEY="YOUR_API_KEY_HERE"
export BINANCE_SECRET_KEY="YOUR_SECRET_KEY_HERE"
```

---

## Step 3 — Fund Wallet

Transfer exactly **$100 USDT** to your Binance Spot wallet.  
No more — the runner hard-caps at MAX_POSITION_USDT=100.0.

---

## Step 4 — Dry-Run Verify (1 min)

```bash
cd C:\Users\admin\workspace\digital-immortality
python trading/mainnet_runner.py --tick --dry-run
```

Expected: sees credentials, fetches BTC price, prints signal (LONG/FLAT/SHORT), prints `[DRY-RUN] Order not placed`.

---

## Step 5 — Go Live

```bash
python trading/mainnet_runner.py --tick
```

Check status:
```bash
python trading/mainnet_runner.py --status
python trading/mainnet_runner.py --report
```

---

## Step 6 — Set Daily Loop (optional)

```bash
python trading/mainnet_runner.py --loop 86400
```

Or use existing cron infrastructure: `cron_daily_tick.bat` already registered for testnet. Duplicate for mainnet.

---

## Kill Conditions (auto-enforced)

| Condition | Threshold | Trades Required |
|-----------|-----------|-----------------|
| Max Drawdown | >10% | any |
| Win Rate | <35% | ≥5 |
| Profit Factor | <0.85 | ≥5 |

If any condition triggers, runner stops and logs `KILL_CONDITION_MET`. Do not restart without post-mortem.

---

## Log Location

`results/mainnet_log.jsonl` — append-only, every tick recorded.

---

## Rollback

If anything is wrong: sell all BTC to USDT manually on Binance, revoke API key, file post-mortem.

---

*Generated: 2026-04-09 | Cycle 115 | Branch 1.1*
