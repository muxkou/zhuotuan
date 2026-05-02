# 阶段一 模块五：正式游玩回合编排验证

## 1. 模块目标

验证最关键的运行时链路：玩家行动输入后，后端能否稳定完成判定、叙事与状态更新。

这是阶段一最核心模块。

---

## 2. 建议代码落点

```text
backend/app/application/orchestrators/turn_resolution_orchestrator.py
backend/app/application/services/action_parser_service.py
backend/app/application/services/roll_decision_service.py
backend/app/application/services/consequence_narration_service.py
backend/app/application/services/runtime_state_service.py
backend/app/domain/schemas/turn.py
backend/app/prompts/action_interpretation.md
backend/app/prompts/consequence_narration.md
```

---

## 3. 输入 contract

```python
class TurnInput(BaseModel):
    case_id: str
    table_id: str
    session_id: str
    turn_index: int
    actor_id: str
    actor_role: Literal["player"]
    player_text: str
    visible_state_snapshot: dict
```

运行依赖：

- `RuleSetSchema`
- `WorldSchema`
- `ModuleBlueprintSchema`
- `SessionRuntimeState`

---

## 4. 输出 contract

```python
class TurnResolutionOutput(BaseModel):
    turn_record: TurnRecordSchema
    updated_runtime_state: dict
    player_visible_updates: dict
    hidden_updates: dict
```

---

## 5. 核心编排步骤

```python
class TurnResolutionOrchestrator:
    async def resolve_turn(self, turn_input: TurnInput, runtime_state: SessionRuntimeState) -> TurnResolutionOutput: ...
```

内部必须显式分步：

1. `parse_player_action`
2. `classify_action_type`
3. `decide_roll_needed`
4. `select_attribute_and_skill`
5. `compute_difficulty`
6. `roll_and_grade`
7. `build_state_delta`
8. `generate_narration`
9. `persist_turn_artifact`

---

## 6. 关键判定规则

### 是否需要掷骰

需要掷骰的情况：

1. 结果不确定
2. 失败会有后果
3. 与环境或 NPC 对抗

不需要掷骰的情况：

1. 明显可见信息
2. 没有风险的简单动作
3. 合理且不受阻的重复尝试

### 失败处理

禁止“纯失败无推进”，失败至少满足其一：

1. 获得部分信息
2. 推进倒计时
3. 触发代价
4. 暴露位置或惊动 NPC

---

## 7. 建议脚本

1. `scripts/phase1/run_turn_resolution_demo.py`
2. `scripts/phase1/replay_turn_sequence.py`
3. `scripts/eval/eval_turn_outcomes.py`
4. `scripts/perf/perf_turn_resolution.py`

示例：

```bash
uv run python scripts/phase1/run_turn_resolution_demo.py \
  --input artifacts/cases/turn_input_001.json \
  --state artifacts/sessions/rainy_town_runtime.json \
  --output artifacts/sessions/rainy_town_turn_001.json
```

---

## 8. 产出

- `artifacts/sessions/<case_id>_turn_001.json`
- `artifacts/sessions/<case_id>_timeline.json`
- `artifacts/evals/turn_eval_summary.json`

---

## 9. 测试要求

至少准备 30 个标准行动样例，覆盖：

1. 观察
2. 调查
3. 交涉
4. 潜行
5. 帮助队友
6. 高风险探索
7. 明显不需要掷骰的动作

检查：

1. 行动分类准确率
2. 掷骰触发正确率
3. 状态更新完整性
4. 失败推进率

---

## 10. 完成标准

1. 玩家输入可分类到核心行动类型
2. 代码独立完成骰点、修正、难度、结果等级计算
3. 连续 10 回合回放中状态不一致次数为 0
4. 单回合结算 P95 < 6s
