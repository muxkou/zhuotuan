# 阶段一 模块四：Session 0 组织与开局准备验证

## 1. 模块目标

验证后端是否能把模组和多名玩家角色组织成“可正式开场”的房间准备数据。

---

## 2. 建议代码落点

```text
backend/app/application/services/session_zero_service.py
backend/app/application/orchestrators/hook_binding_orchestrator.py
backend/app/prompts/session_zero_summary.md
```

---

## 3. 输入 contract

```python
class RoomPreference(BaseModel):
    room_name: str
    player_count: int
    ai_style: str
    allow_character_death: bool
    allow_pvp: bool
    horror_level: str
    humor_level: str
    taboo_topics: list[str] = []
```

附加输入：

- `WorldSchema`
- `ModuleBlueprintSchema`
- `list[CharacterReviewReport]`

---

## 4. 输出 contract

```python
class CharacterHookBinding(BaseModel):
    character_id: str
    public_motivation: str
    hidden_hook: str | None = None
    relationship_notes: list[str] = []

class SessionZeroPackage(BaseModel):
    room_preference: RoomPreference
    public_brief: str
    safety_and_boundaries: list[str]
    character_bindings: list[CharacterHookBinding]
    public_known_facts: list[str]
    starting_scene_hint: str
```

---

## 5. 核心逻辑

1. 过滤未通过审核角色
2. 为每个角色绑定至少一个模组钩子
3. 生成玩家公开信息
4. 生成系统可见的隐藏钩子
5. 整理统一开场说明

---

## 6. 建议脚本

1. `scripts/phase1/prepare_session_zero.py`
2. `scripts/eval/eval_session_zero_cases.py`

示例：

```bash
uv run python scripts/phase1/prepare_session_zero.py \
  --room artifacts/cases/room_pref.json \
  --world artifacts/worlds/rainy_town_world.json \
  --module artifacts/modules/rainy_town_module.json \
  --characters artifacts/cases/room_characters.json \
  --output artifacts/sessions/rainy_town_session0.json
```

---

## 7. 产出

- `artifacts/sessions/<case_id>_session0.json`
- `artifacts/sessions/<case_id>_public_brief.md`
- `artifacts/sessions/<case_id>_kp_brief.md`

---

## 8. 测试要求

检查：

1. 2-4 名角色都能得到明确开局动机
2. 每名角色至少绑定 1 个模组钩子
3. 公开信息不过度剧透
4. 房间边界被正确记录

性能：

- 4 人 Session 0 准备 P95 < 10s

---

## 9. 完成标准

1. 可输出公开版和隐藏版准备材料
2. 各角色参与动机明确
3. 正式游玩前不再需要手工拼接开场信息
