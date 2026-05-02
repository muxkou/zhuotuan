# 阶段一 模块三：角色生成与审核链路验证

## 1. 模块目标

验证“玩家问卷 -> 角色草案 -> 规则审核 -> 世界观审核 -> 模组适配审核”的完整链路。

---

## 2. 建议代码落点

```text
backend/app/application/services/character_generation_service.py
backend/app/application/validators/character_rules_validator.py
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
```

附加输入：

- `WorldSchema`
- `ModuleBlueprintSchema`
- `RuleSetSchema`

---

## 4. 输出 contract

```python
class CharacterReviewReport(ValidationReport):
    review_result: Literal["approved", "needs_revision", "warning", "enhance"]
    normalized_character: CharacterSheetSchema | None = None
    blocking_reasons: list[str] = []
    revision_suggestions: list[str] = []
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
    ) -> CharacterReviewReport: ...
```

审核顺序：

1. 规则审核
2. 世界观审核
3. 模组适配审核

---

## 6. 建议脚本

1. `scripts/phase1/generate_character_draft.py`
2. `scripts/phase1/review_character_sheet.py`
3. `scripts/eval/eval_character_review.py`
4. `scripts/perf/perf_character_pipeline.py`

示例：

```bash
uv run python scripts/phase1/review_character_sheet.py \
  --input artifacts/characters/reporter_draft.json \
  --world artifacts/worlds/rainy_town_world.json \
  --module artifacts/modules/rainy_town_module.json \
  --output artifacts/characters/reporter_review.json
```

---

## 7. 审核规则

### 规则审核

- 属性点总额是否超限
- 技能点总额是否超限
- 必填字段是否缺失

### 世界观审核

- 是否拥有不允许的强超自然能力
- 是否明显违背世界常识

### 模组适配审核

- 是否提前知道核心秘密
- 是否没有参与动机
- 是否无法与其他玩家协作

---

## 8. 产出

- `artifacts/characters/<case_id>_draft.json`
- `artifacts/characters/<case_id>_review.json`
- `artifacts/evals/character_batch_summary.json`

---

## 9. 测试要求

至少准备：

1. 合理角色 5 个
2. 剧透角色 5 个
3. 超能力角色 5 个
4. 无动机角色 5 个

检查：

1. 错误角色识别召回率
2. 合理角色误杀率
3. 修改建议可用性

---

## 10. 完成标准

1. 角色草案可被统一 schema 接收
2. 审核结果包含 `approved/needs_revision/warning/enhance`
3. 错误角色识别召回率 >= 85%
4. 单角色全链路 P95 < 8s
