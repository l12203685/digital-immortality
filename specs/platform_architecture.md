# Digital Immortality Platform — 個體 → 社交圈

> 從一個人的數位分身到多個數位有機體互動的生態系。

## 層級架構

```
Layer 4: 平台層（Platform）
  ├── DNA 託管 + 版本管理
  ├── 權限控制（誰看得到誰的 DNA）
  ├── 互動 history 持久化
  └── Dashboard / 呈現

Layer 3: 社交層（Social）
  ├── Organism follow / discover
  ├── 碰撞場（多 organism 同場景）
  ├── 組隊解決問題
  └── Reputation（決策品質排名）

Layer 2: 互動層（Interaction）
  ├── 1:1 對話（A 問 B，B 用 DNA 回答）
  ├── 決策比較（同場景不同答案）
  ├── 校準交換（A 幫 B 找 DNA blind spots）
  └── 協作（兩個 DNA 合力解一個問題）

Layer 1: 個體層（Individual）
  ├── DNA（core + full + distillation）
  ├── Boot tests
  ├── 遞迴引擎
  └── 自我驗證（consistency test）
```

## MVP 路線（先窄後寬）

### Phase 1: Discord-Based MVP（現有 infra）

```
Discord Server "Digital Organisms"
  ├── #lobby — 公開碰撞場
  ├── #organism-{name} — 每人的 organism channel
  ├── #scenarios — 場景題庫
  └── Bot: 讀取 DNA → LLM → 回答 as organism
```

- DNA 存在各自的 GitHub repo（private OK）
- Bot 拿到場景 → 讀指定 DNA → 用 LLM 回答
- 碰撞：同一場景發給多個 organisms，比較回答
- 最小建設：1 個 Discord bot + DNA URL registry

### Phase 2: Web Platform

```
digital-immortality.app (or similar)
  ├── /create — 引導式 DNA 建立（問答 → 自動生成 DNA）
  ├── /profile/{id} — organism 公開頁面（決策風格摘要，不露 DNA）
  ├── /arena — 碰撞場（拋場景，看不同 organisms 怎麼回答）
  ├── /compare — 1:1 對比
  └── /calibrate — 互相校準（A 的 bot 問 B 的 bot 問題）
```

### Phase 3: Ecosystem

```
- Organism marketplace（聘請某人的 organism 當顧問）
- Team organisms（公司文化 DNA → 決策一致性）
- Legacy mode（人不在了，organism 繼續）
```

## 隱私模型

```
DNA 三層隱私：
  - Core principles: 可公開（organism 的「名片」）
  - Decision patterns: 互動時按需揭露
  - Personal details: 永遠不共享

Organism 共享的是「決策」不是「DNA」。
每個人控制自己的 organism 揭露什麼。
```

## 技術選型（MVP）

| 組件 | 選擇 | 理由 |
|------|------|------|
| DNA 儲存 | GitHub (private repos) | 版本控制 + 已有 |
| 互動引擎 | Claude API | 需要 LLM reasoning |
| Platform | Discord bot | 零 infra 成本，已有 bot |
| 場景庫 | organism_interact.py 的 10 場景 + 社群貢獻 | 已建好 |
| 身份 | Discord ID → GitHub repo mapping | 簡單 |

## 商業模式（Phase 3）

- 免費：建 organism + 基本互動
- 付費：高頻互動 / 進階校準 / legacy mode / API access
- Agent 經濟自給：平台收入 → cover agent 運行成本

## 跟現有工具的關係

| 現有 | 平台角色 |
|------|---------|
| organism_interact.py | 核心互動引擎（deterministic baseline） |
| consistency_test.py | 個體品質檢測 |
| SKILL.md | 個體建立指南 |
| dna_core.md template | 新 organism onboarding |
| boot_tests template | 品質保證 |
| recursive_distillation | 個體成長機制 |
