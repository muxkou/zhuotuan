# 阶段一 模块三：角色生成与审核链路验证

## 1. 模块目标

验证“玩家问卷 -> 角色草案 -> 规则审核 -> 世界车卡约束审核 -> 世界观审核 -> 模组适配审核 -> 房间顺序审核”的完整链路。

---

## 2. 建议代码落点

```text
backend/app/application/services/character_generation_service.py
backend/app/application/services/manual_character_card_service.py
backend/app/application/services/character_roster_review_service.py
backend/app/application/validators/character_rules_validator.py
backend/app/application/validators/character_world_profile_validator.py
backend/app/application/validators/character_world_validator.py
backend/app/application/validators/character_module_validator.py
backend/app/prompts/character_generation.md
backend/app/prompts/character_repair.md
```

---

## 3. 输入 contract

```python
class CharacterQuestionnaire(BaseModel):
    case_id: str
    player_id: str
    name_hint: str | None = None
    identity_answer: str
    motivation_answer: str
    specialty_answer: str
    fear_answer: str
    relationship_answer: str | None = None
    secret_answer: str | None = None

class ManualCharacterCardInput(BaseModel):
    case_id: str
    player_id: str
    name: str
    identity: str
    concept: str
    personality_tags: list[str]
    module_motivation: str
    attributes: dict[str, int]
    skills: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    fears: list[str]
    secret: str | None = None
    relationships: list[dict[str, str]]
    inventory: list[str]
```

附加输入：

- `WorldSchema`
- `ModuleBlueprintSchema`
- `RuleSetSchema`
- `list[CharacterReviewReport]` 或 `list[CharacterSheetSchema]`
  - 表示同一房间中已经审核通过的前序玩家角色

---

## 4. 输出 contract

```python
class CharacterReviewReport(ValidationReport):
    review_result: Literal["approved", "needs_revision", "warning", "enhance"]
    normalized_character: CharacterSheetSchema | None = None
    blocking_reasons: list[str] = []
    revision_suggestions: list[str] = []
    queue_position: int | None = None
    roster_conflicts: list[str] = []
```

---

## 5. 核心 service

```python
class CharacterGenerationService:
    async def generate(
        self,
        questionnaire: CharacterQuestionnaire,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
    ) -> CharacterSheetSchema: ...

class CharacterReviewPipeline:
    def review(
        self,
        character: CharacterSheetSchema,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
        existing_characters: list[CharacterSheetSchema] = [],
    ) -> CharacterReviewReport: ...

class ManualCharacterCardService:
    def build_character(
        self,
        manual_input: ManualCharacterCardInput,
        world: WorldSchema,
    ) -> CharacterSheetSchema: ...
```

审核顺序：

1. 规则审核
2. 世界车卡约束审核
3. 世界观审核
4. 模组适配审核
5. 房间顺序审核

房间顺序审核要求：

1. 同一房间内，角色审核必须串行执行，不能并行放行。
2. 第 `N` 个角色审核时，要读取前 `N-1` 个已通过角色。
3. 必须检查：
   - 身份是否互斥
   - 关系与秘密是否直接冲突
   - 是否重复占用唯一叙事槽位
   - 是否导致队伍合作前提断裂

---

## 6. 建议脚本

1. `scripts/phase1/generate_character_draft.py`
2. `scripts/phase1/review_character_sheet.py`
3. `scripts/phase1/review_manual_character_card.py`
4. `scripts/phase1/review_character_roster_queue.py`

示例：

```bash
uv run python scripts/phase1/review_character_sheet.py \
  --input artifacts/characters/reporter_draft.json \
  --world artifacts/worlds/rainy_town_world.json \
  --module artifacts/modules/rainy_town_module.json \
  --output artifacts/characters/reporter_review.json

uv run python scripts/phase1/review_manual_character_card.py \
  --input artifacts/characters/reporter_manual_card.json \
  --world artifacts/worlds/rainy_town_world.json \
  --profile artifacts/worlds/rainy_town_character_profile.json \
  --module artifacts/modules/rainy_town_module.json \
  --output artifacts/characters/reporter_manual_review.json
```

---

## 7. 审核规则

### 规则审核

- 属性点总额是否超限
- 必填字段是否缺失

### 世界车卡约束审核

- 角色属性是否全部出自世界允许的属性定义
- 每个属性是否落在该世界定义的取值范围内
- 特殊属性是否被正确识别
- 角色技能是否全部来自世界技能表
- 技能值是否固定为 `0/1/2`
- 技能点总额是否超过世界 `total_skill_points`
- 角色描述是否与世界给定的属性语义相匹配
- 是否使用了世界禁止的车卡元素

说明：

1. 技能由 `WorldSchema.character_creation_profile.skills` 定义。
2. 玩家手动填写车卡时，必须提交结构化 `attributes` 和 `skills`。
3. 手动车卡与 LLM 生成角色共用同一套审核 pipeline。

### 世界观审核

- 是否拥有不允许的强超自然能力
- 是否明显违背世界常识
- 是否无视世界特殊状态约束

### 模组适配审核

- 是否提前知道核心秘密
- 是否没有参与动机
- 是否无法与其他玩家协作
- 是否与已通过角色相互矛盾
- 是否超出模组当前允许的玩家人数上限

---

## 8. 产出

- `artifacts/characters/<case_id>_draft.json`
- `artifacts/characters/<case_id>_review.json`
- `artifacts/characters/<case_id>_manual_review.json`
- `artifacts/characters/<case_id>_roster_review.json`

---

## 9. 测试要求

至少准备：

1. 合理角色 5 个
2. 剧透角色 5 个
3. 超能力角色 5 个
4. 无动机角色 5 个
5. 互相矛盾角色 5 组
6. 超出人数上限角色 5 组

检查：

1. 错误角色识别召回率
2. 合理角色误杀率
3. 修改建议可用性
4. 顺序审核时冲突角色识别率

---

## 10. 完成标准

1. 角色草案可被统一 schema 接收
2. 审核结果包含 `approved/needs_revision/warning/enhance`
3. 错误角色识别召回率 >= 85%
4. 顺序审核时可稳定考虑前序角色上下文
5. 手动车卡输入可以不经 LLM 生成，直接进入审核链路
