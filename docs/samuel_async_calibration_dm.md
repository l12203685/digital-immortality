# Samuel Async Calibration DM

> Draft DM to send Samuel for async calibration (no scheduling required)
> Based on SOP #45 Stage 3: Async Calibration Protocol
> Created: 2026-04-09 UTC (cycle 207)
> Send via: WhatsApp / LINE / preferred channel

---

## Context (internal — don't send)

Samuel and I have a collision engine running. 22 scenarios, 15/22 AGREE. The 7 divergences are all social.

The async calibration goal:
- Minimum: 3 corrected scenarios + 1 new principle extracted
- Tests the 3 highest-information-value divergence domains from the collision
- No scheduling, no coordination — just send and wait

The 3 scenarios target:
1. `relationship_downgrade` — where we most clearly diverge
2. `network_roi` — unilateral vs direct audit
3. `intro_gatekeeping` — his gatekeeping behavior vs mine

---

## DM Text (send as-is)

---

嘿 Samuel，

我在跑一個實驗，需要你幫我校正。3 個情境，每個你只需要回答「你會怎麼做，為什麼」就好。10 分鐘。

**情境 1:**
你有個朋友，以前每週都會聊，最近三個月突然沒什麼聯絡。你沒有跟他吵架或發生什麼事。

你會怎麼處理這個關係？

---

**情境 2:**
你幫一個認識兩年的人介紹了 3 個你網絡裡的人。他每次都有聯絡，結果都很好，但之後你需要幫助的時候，他都「很忙」，沒有回應。

你現在怎麼看這段關係？你會做什麼？

---

**情境 3:**
你的一個非常好的朋友，請你把他介紹給你工作圈裡一個你很尊重的前輩。你不確定他們是否合得來或互相有利。

你會怎麼做？

---

沒有「正確答案」。我在測試我對你的模型準不準。

---

## Expected Use

1. Edward pastes this DM to Samuel (WhatsApp/LINE)
2. Samuel replies with his actual behavior in each scenario
3. Edward records corrections in `templates/samuel_dna.md` §4 or §6
4. Edward re-runs collision: `python organism_interact.py templates/dna_core.md templates/samuel_dna.md --report`
5. Update dynamic_tree.md with new agreement rate

## Success Criteria

- ≥1 correction that changes a AGREE→DIVERGE or DIVERGE→AGREE
- ≥1 new principle extracted and added to samuel_dna.md
- Collision re-run confirms changed rate

## Next Steps After Response

If Samuel confirms `relationship_downgrade = quiet withdrawal`:
→ This is DIVERGE vs Edward (direct conversation) → keep as documented divergence

If Samuel corrects `intro_gatekeeping`:
→ Rewrite samuel_dna.md §6 Social Operating Rules, re-run collision

---

*2026-04-09 UTC (cycle 207)*
