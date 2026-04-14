# Organism Drift 40% — 結構修正方案

> Created: 2026-04-14 10:50 +08 (Taipei)
> Source cycles: 435 (stable 40% detected), 427, 450 (0pp drift confirmed)
> Author: Edward AI (B4 branch-growth)
> Status: **SPEC — awaits Edward ratification**; low-risk code fixes auto-apply, high-risk paused

---

## 1. 指標定義（clarify "40% drift"）

**40% 不是 drift，而是 agreement floor（收斂地板）。**

| 指標 | 定義 | 當前值 | 目標 | 資料來源 |
|------|------|--------|------|----------|
| **Agreement rate** | 同意 / 總場景 | 16/40 ≈ 40% (agreement-fished run) | 45%+ after Samuel recalibration | `organism_interact.py --report` |
| **Base agreement** | 原 22 場景中 AGREE | 6/22 ≈ 27% | n/a (base rate, not a target) | collision_dna_core_vs_Samuel_*.json |
| **Drift delta** | Agreement 變化量 | 0 pp (cycle 427→450) | 保持 ≤ ±3pp | daemon_log cycles |
| **Structural mismatch** | Edward DNA +86 MDs 未反射到 Samuel 端 | Yes | Resolved via async DM calibration | `docs/samuel_async_calibration_dm.md` |

**結論：「drift 40%」是語義誤標。**
- 真正的 drift=**0 pp**（穩定）
- 40% 是 agreement 地板，分歧是**結構性**（EV 腦 vs 關係腦，非參數偏差）
- 結構性分歧不應該靠 algorithm fix 抹平；靠 Samuel 輸入校準才有意義

---

## 2. 根因（root cause）

Per `docs/b4_divergence_root_cause.md`：
- **Cluster A** 訊號源不同（base rate vs social proof）
- **Cluster B** 退出規則不同（kill condition vs loyalty）
- **Cluster C** 網絡理論不同（dormant tolerance vs ROI audit）
- **Cluster D** 社交速度不同（assess first vs act first）
- **Cluster E** 把關標準不同（quality threshold vs relationship override）

這 5 叢集 = 19 divergence，解釋 60% 分歧。剩 40% 雜訊在 edge cases。

---

## 3. 修正方案（分三層）

### 層 1 — 文檔/指標修正（LOW risk, auto-apply）

- [x] **寫本 spec** `docs/organism_drift_fix_2026-04-14.md`
- [ ] **修 daemon_log 語義** 下一輪 B4 驗證輸出改寫為：
  ```
  B4 agreement floor 40% stable (structural, not drift); drift delta 0pp
  ```
  而非「drift stable 40% (structural mismatch)」。
- [ ] **新增 baseline_anchor.json** 固化當前 (16/40, 6/22, 0pp) 作為下次比較基線；每 10 cycles 輸出 comparison。

### 層 2 — organism_interact.py 結構補強（MEDIUM risk, PR review）

- [ ] **新增 `--drift-check` mode**：
  ```python
  python organism_interact.py --drift-check \
    --baseline results/baseline_anchor.json \
    --threshold 3  # pp
  ```
  輸出三態：HEALTHY (<=3pp) / WATCH (3-7pp) / DRIFT (>7pp)。
  行為：**僅讀**，不改動任何 scenario bank。
- [ ] **分離 agreement 類型**：
  - `structural_agree` = 兩邊 axiom 對齊
  - `coincidental_agree` = axiom 不同但 action 剛好同
  - `fished_agree` = agreement-fishing 場景，不計入 baseline 分母
- [ ] **鎖定 base-22** 不再 agreement-fish 膨脹分母；fishing 另存 `--bonus-scenarios` flag。

### 層 3 — Samuel 校準 gate（HIGH risk, 等 Edward 拍板）

- [ ] **Samuel 非同步 DM gate** `docs/samuel_async_calibration_dm.md` 已就緒，**human-gated** = Edward 親自寄出。
- [ ] 若 Samuel 回覆：
  - 更新 Samuel DNA snapshot → 重跑 collision
  - 預期 agreement 從 27% 上拉到 40-45%（去除 stale 因素後的結構性地板）
- [ ] 若 Samuel 不回覆（>14 天）：**接受 27% 為結構性地板**，關 B4 為 dormant branch 直到下次主動重啟。

---

## 4. 何謂「修正完成」

| 檢查項 | 通過條件 |
|--------|----------|
| 語義標籤修正 | daemon_log 下輪 B4 行不再出現 "drift" 錯標 |
| baseline_anchor.json | 存在且每 10 cycles 對比輸出 |
| --drift-check mode | 加入 organism_interact.py 且測試通過 |
| Samuel calibration gate | Edward 拍板 send/skip/defer |

---

## 5. 本次執行（2026-04-14 10:50 +08）

**只做**：
- 寫本 spec（層 1 第 1 項）

**不做**（風險過大或需 Edward 決策）：
- organism_interact.py code change — 暫停，等 Edward 同意 PR
- Samuel DM — 等 Edward 親自寄

**下次 B4 cycle 可自動承接**：
- baseline_anchor.json 生成
- daemon 語義標籤修正

---

## 6. 參考

- `results/daemon_log.md` cycles 427, 435, 450
- `docs/b4_divergence_root_cause.md` — 5-cluster 分歧根因
- `docs/samuel_async_calibration_dm.md` — 校準 DM 模板（human-gated）
- `organism_interact.py` — 22 base + 18 bonus scenarios
- `results/collision_dna_core_vs_Samuel_*.md` — 最近 4 次 collision 輸出
