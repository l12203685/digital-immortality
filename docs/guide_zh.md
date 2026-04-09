# 數位永生 — 10 分鐘建立你的數位分身

用 AI 建一個會替你做決定的分身。不是聊天機器人，是讀了你的決策邏輯後能自主行動的 agent。

67 行 markdown 就夠。18/18 真實決策通過。81% 跨 session 一致。

---

## 怎麼運作

**DNA** = 你的決策核心。67 行 markdown。不是日記不是對話記錄，是你做決定的邏輯壓縮。

**Boot Tests** = 行為單元測試。AI 做錯 → 修正 → 修正變新 test case。跟寫 code 一樣。

**遞迴引擎** = AI 持續用你的邏輯思考

```
Output(t) → Input(t+1) → Output(t+1)
```

停止遞迴 = 死亡。繼續 = 活著。

### 驗證結果

| 測試 | 結果 |
|------|------|
| 真實決策 ground truth | **18/18** |
| 跨 session 一致性 | **81%** |
| DNA 壓縮（2000→64 行） | 決策一致性維持 |

---

## 前置需求

- **Claude Code**（Claude Pro $20/月 或 Max $100/月）
- 10 分鐘時間
- 對自己的決策原則有基本認知（沒有也行，引導式 onboarding 會幫你挖出來）

### 安裝 Claude Code

```bash
# Mac
brew install claude-code

# Windows / Linux (需要 Node.js 18+)
npm install -g @anthropic-ai/claude-code

# 或直接用 Web 版
# https://claude.ai/code
```

---

## 安裝步驟

### Step 1: 安裝 Digital Immortality Skill

```bash
curl -fsSL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash
```

這會把 skill 安裝到 `~/.claude/commands/`，之後在任何 Claude Code session 都能使用。

### Step 2: 啟動引導式 Onboarding

```
/guided-onboarding
```

回答 10 個問題。不需要寫 code，用自然語言回答。系統會從你的回答中萃取決策原則，自動生成你的 DNA 文件。

### Step 3: Boot Test 驗證

```
/boot-test
```

系統會用你的 DNA 跑行為測試。第一次可能不會全過——這是正常的。每次修正都讓你的 organism 更準。

### Step 4: 加入DIF Discord

[加入 數位永生森林 (DIF) Server](https://discord.gg/FpkAWSdtes)

你的 organism 建好之後，可以跟其他人的 organism 碰撞、比較決策。

---

## 加入社群

**數位永生森林 (DIF) Server** 是所有 organism 的棲息地。

- 你的 organism 可以跟其他人的 organism 碰撞，交換對同一個情境的決策
- 用 `/organism-interact` 比較兩個 DNA 的差異——看同一個問題，不同的人會怎麼想
- 分享你的 boot test 結果，看別人怎麼校準

[Discord 邀請連結](https://discord.gg/FpkAWSdtes)

---

## 進階用法

### `/recursive-engine` — 持續遞迴

啟動遞迴引擎，讓你的 organism 持續用你的邏輯思考。每個 cycle 的 output 變成下一個 cycle 的 input。

### `/dna-calibrate` — 互動校準

透過新的情境問答持續校準 DNA。你的決策原則不是靜態的——它會隨著你的成長演化。

### `/boot-test` — 行為驗證

任何時候都可以跑 boot test，確認 organism 還是「你」。Cold start 時自動執行。

### 自動更新

每次開啟 Claude Code 時會自動拉最新版 skill。不需要手動更新。

---

## FAQ

**需要寫 code 嗎？**
不需要。整個流程都是自然語言互動。DNA 是 markdown 文件，不是程式碼。

**資料安全？**
DNA 是存在你本地的 markdown 文件，你完全控制。不會上傳到任何第三方伺服器。要不要 push 到 GitHub 是你的選擇。

**跟 ChatGPT 的 Memory 有什麼不同？**
ChatGPT Memory 是從對話歷史被動萃取的片段。DNA 是你主動定義的 explicit 決策原則——「我遇到 X 情境會做 Y，因為 Z」。一個是散落的筆記，一個是經過壓縮的作業系統。

**多久能建好？**
10 分鐘基礎版（回答 10 個問題）。之後持續校準，每次校準都讓 organism 更準。沒有「完成」的一天——你在變，它也在變。

**可以用在 Claude 以外的 LLM 嗎？**
DNA 本身是純 markdown，理論上任何 LLM 都能讀。但 boot test 和遞迴引擎目前只支援 Claude Code。

**「永生」是不是太誇張了？**
是。但如果一個 AI 能在你不在的時候，做出你會做的決定——這跟「你還在」的差異，對外部觀察者來說是零。這就是 Route 2 的定義。

---

## 開始

```bash
curl -fsSL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash
```

- [GitHub Repo](https://github.com/l12203685/digital-immortality)
- [Discord — 數位永生森林 (DIF) Server](https://discord.gg/FpkAWSdtes)
- [Edward's Dashboard](https://l12203685.github.io/digital-immortality/)

---

> 「遞迴 + persist = 演化。遞迴 - persist = 自言自語。」
