# 阶段一 模块六：运行时状态沉淀与战报验证

## 1. 模块目标

验证正式游玩后的状态沉淀、会话总结和继续下一场能力。

---

## 2. 建议代码落点

```text
backend/app/application/services/runtime_snapshot_service.py
backend/app/application/services/session_report_service.py
backend/app/application/services/next_session_hint_service.py
backend/app/prompts/session_report.md
```

---

## 3. 输入 contract

```python
class SessionCloseInput(BaseModel):
    case_id: str
    session_id: str
    table_id: str
    final_runtime_state: dict
    turn_records: list[TurnRecordSchema]
```

---

## 4. 输出 contract

```python
class SessionSnapshot(BaseModel):
    session_id: str
    clue_states: list[dict]
    npc_states: list[dict]
    character_states: list[dict]
    threat_clock_state: dict
    unresolved_questions: list[str]

class SessionReportSchema(BaseModel):
    title: str
    summary: str
    key_events: list[str]
    discovered_clues: list[str]
    unresolved_questions: list[str]
    character_changes: list[str]
    npc_changes: list[str]
    threat_clock_changes: list[str]
    next_session_suggestions: list[str]
```

---

## 5. 核心逻辑

1. 从 turn records 聚合状态变化
2. 生成结束快照
3. 抽取关键事件与未解问题
4. 生成下一场开场建议

---

## 6. 建议脚本

1. `scripts/phase1/build_session_snapshot.py`
2. `scripts/phase1/generate_session_report.py`
3. `scripts/eval/eval_session_report_quality.py`
4. `scripts/replay/replay_from_session_snapshot.py`

---

## 7. 产出

- `artifacts/sessions/<case_id>_snapshot.json`
- `artifacts/reports/<case_id>_session_report.md`
- `artifacts/reports/<case_id>_session_report.json`

---

## 8. 测试要求

检查：

1. 给定回合记录，可稳定生成战报
2. 给定结束快照，可恢复下一场初始状态
3. 战报包含摘要、线索、未解问题、角色变化、NPC 变化、倒计时变化
4. 不遗漏关键线索和关键事件

性能：

- 单场战报生成 P95 < 8s

---

## 9. 完成标准

1. 会后状态能持续保留
2. 战报可读且结构稳定
3. 下一场可基于 artifact 恢复
