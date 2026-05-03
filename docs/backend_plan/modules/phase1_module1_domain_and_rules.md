# 阶段一 模块一：领域模型与轻规则骨架

## 1. 模块目标

冻结第一版核心 schema、枚举和值对象，让后续所有脚本和 API 都基于同一套 contract 开发。

先读：

- `docs/backend_plan/development_conventions.md`

本模块不接入 LLM，不做 API。

---

## 2. 建议代码落点

```text
backend/app/domain/enums/game.py
backend/app/domain/schemas/common.py
backend/app/domain/schemas/ruleset.py
backend/app/domain/schemas/world.py
backend/app/domain/schemas/module.py
backend/app/domain/schemas/character.py
backend/app/domain/schemas/session.py
backend/app/domain/value_objects/dice.py
backend/app/application/validators/schema_validator.py
```

---

## 3. 输入 contract

输入为人工编写的最小样例 JSON / YAML：

- `world`
- `module`
- `character`
- `session_snapshot`

---

## 4. 输出 contract

输出包括：

1. Pydantic schema 集合
2. 枚举定义
3. 基础规则计算函数
4. 可通过校验的样例 artifact
5. schema regression 报告

---

## 5. 关键 schema 结构

### `RuleSetSchema`

```python
class AttributeScore(BaseModel):
    physique: int
    agility: int
    mind: int
    willpower: int
    social: int

class SkillBonus(BaseModel):
    investigation: int = 0
    negotiation: int = 0
    stealth: int = 0
    combat: int = 0
    medicine: int = 0
    occult: int = 0
    craft: int = 0
    survival: int = 0

class RuleSetSchema(BaseModel):
    id: str
    version: str
    name: str
    description: str
    dice_formula: Literal["2d6"]
    difficulty_bands: dict[str, int]
    attributes: list[str]
    skills: list[str]
    resource_rules: dict[str, int | str]
```

### `WorldSchema`

```python
class AttributeSemanticBand(BaseModel):
    min_value: int
    max_value: int
    summary: str
    examples: list[str] = []

class AttributeDefinition(BaseModel):
    key: str
    label: str
    description: str
    min_value: int
    max_value: int
    semantic_bands: list[AttributeSemanticBand]
    is_core: bool = True

class SpecialStatusDefinition(BaseModel):
    key: str
    label: str
    description: str
    trigger_sources: list[str]
    behavioral_constraints: list[str]
    recovery_hints: list[str] = []

class CharacterCreationProfile(BaseModel):
    base_attributes: list[AttributeDefinition]
    world_specific_attributes: list[AttributeDefinition] = []
    total_attribute_budget_min: int
    total_attribute_budget_max: int
    identity_guidelines: list[str]
    forbidden_character_elements: list[str] = []

class WorldSchema(BaseModel):
    id: str
    version: str
    name: str
    tagline: str
    genre: str
    era: str
    tone: list[str]
    public_rules: list[str]
    hidden_rules: list[str] = []
    factions: list[str]
    common_locations: list[str]
    taboos: list[str]
    recommended_roles: list[str]
    narration_style: dict[str, str | int]
    character_creation_profile: CharacterCreationProfile
    special_status_catalog: list[SpecialStatusDefinition] = []
```

### `ModuleBlueprintSchema`

```python
class ClueLink(BaseModel):
    clue_id: str
    target_secret_id: str
    location_id: str | None = None
    fallback_clue_ids: list[str] = []

class ModuleBlueprintSchema(BaseModel):
    id: str
    version: str
    world_id: str
    name: str
    player_count_min: int
    player_count_max: int
    duration_minutes: int
    opening_hook: str
    core_secret: str
    major_conflict: str
    required_npcs: list[str]
    key_locations: list[str]
    key_clues: list[ClueLink]
    threat_clock_id: str
    endings: dict[str, str]
    ai_do_not_change: list[str]
    ai_freedom_level: Literal["conservative", "standard", "high"]
```

### `CharacterSheetSchema`

```python
class CharacterSheetSchema(BaseModel):
    id: str
    version: str
    name: str
    identity: str
    concept: str
    personality_tags: list[str]
    module_motivation: str
    attributes: AttributeScore
    skills: SkillBonus
    strengths: list[str]
    weaknesses: list[str]
    fears: list[str]
    secret: str | None = None
    relationships: list[dict[str, str]]
    inventory: list[str]
```

说明：

1. 角色卡中的 `attributes` 不再只是假定 5 维固定属性。
2. 当前阶段实现允许仍以基础 5 维为默认参考，但世界必须显式提供这些属性定义和解释。
3. 世界可以增加特殊属性，例如：
   - `faith`
   - `pollution_resistance`
   - `spirit_sensitivity`
4. 世界也可以不增加特殊属性，只使用基础属性集。

### `TurnRecordSchema`

```python
class TurnRecordSchema(BaseModel):
    id: str
    turn_index: int
    actor_type: Literal["player", "kp", "system"]
    actor_id: str
    player_input: str | None = None
    interpreted_action_type: str | None = None
    roll_required: bool
    roll_formula: str | None = None
    roll_total: int | None = None
    difficulty: int | None = None
    resolution_grade: Literal["critical_success", "success", "mixed", "failure", "critical_failure"] | None = None
    consequence_summary: str
    state_delta: dict
```

---

## 6. 核心纯函数

```python
def validate_attributes(attrs: AttributeScore) -> list[ErrorItem]: ...
def validate_attributes_against_world(
    attrs: dict[str, int],
    world_profile: CharacterCreationProfile,
) -> list[ErrorItem]: ...
def validate_skill_budget(skills: SkillBonus) -> list[ErrorItem]: ...
def roll_2d6(seed: int | None = None) -> tuple[int, list[int]]: ...
def compute_check_total(base_roll: int, attribute_mod: int, skill_mod: int) -> int: ...
def grade_check_result(total: int, difficulty: int) -> str: ...
```

---

## 7. 建议脚本

1. `scripts/phase1/build_minimum_schemas.py`
2. `scripts/phase1/validate_sample_assets.py`
3. `scripts/eval/schema_regression.py`

示例：

```bash
uv run python scripts/phase1/validate_sample_assets.py \
  --input artifacts/samples \
  --output artifacts/evals/schema_report.json
```

---

## 8. 产出

- `artifacts/worlds/min_world.json`
- `artifacts/modules/min_module.json`
- `artifacts/characters/min_character.json`
- `artifacts/sessions/min_session_snapshot.json`
- `artifacts/evals/schema_report.json`

---

## 9. 测试要求

### unit

- schema 必填字段缺失时报错
- 属性和技能越界时报错
- 世界车卡属性定义缺失时报错
- 属性语义区间不连续或互相重叠时报错
- 特殊状态定义缺少行为约束时报错
- 骰点函数结果范围正确

### integration

- 最小 world/module/character/session 样例可被统一加载

### golden

- 样例 artifact 字段结构稳定

---

## 10. 完成标准

1. 核心 schema 第一版字段冻结
2. 所有样例 JSON 能通过 schema 校验
3. 世界内已包含可直接供车卡阶段使用的属性与特殊状态约束
4. 单次全量 schema 校验 < 1s
