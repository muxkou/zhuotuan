# 阶段三 模块一：人类 KP 副驾驶脚本能力

## 1. 模块目标

验证 AI 作为人类 KP 辅助工具的后端能力，包括备团、提示、记录与复盘。

---

## 2. 建议代码落点

```text
backend/app/application/services/kp_copilot_service.py
backend/app/prompts/kp_npc_lines.md
backend/app/prompts/kp_clue_reminder.md
backend/app/prompts/kp_action_review.md
```

---

## 3. 输入输出 contract

输入：

- 模组蓝图
- 当前 session runtime state
- 历史 turn records

输出：

- NPC 台词建议列表
- 线索提醒列表
- 玩家行为复盘摘要
- KP 专属战报摘要

---

## 4. 建议脚本

1. `scripts/phase3/suggest_npc_lines.py`
2. `scripts/phase3/remind_missing_clues.py`
3. `scripts/phase3/review_player_actions.py`
4. `scripts/phase3/generate_kp_summary.py`

---

## 5. 完成标准

1. 给定模组和会话记录，可生成可用建议
2. 建议不篡改核心秘密
3. 单次辅助任务 P95 < 8s
