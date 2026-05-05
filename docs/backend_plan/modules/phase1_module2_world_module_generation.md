# 阶段一 模块二：世界与模组生成可行性验证

## 1. 模块目标

验证“快速开团输入 -> 世界草案 -> 模组草案 -> 校验结果”是否稳定可用。

本模块优先验证生成质量，不做 API。

---

## 2. 建议代码落点

```text
backend/app/application/services/world_generation_service.py
backend/app/application/services/character_creation_profile_generation_service.py
backend/app/application/services/module_generation_service.py
backend/app/application/validators/module_playability_validator.py
backend/app/infra/llm/llm_client.py
backend/app/prompts/world_generation.md
backend/app/prompts/character_creation_profile_generation.md
backend/app/prompts/module_generation.md
backend/app/prompts/module_repair.md
```

---

## 3. 输入 contract

```python
class QuickStartInput(BaseModel):
    case_id: str
    genre: str
    duration_minutes: int
    player_count: int
    tone: list[str]
    inspiration: str | None = None
    horror_level: Literal["low", "medium", "high"]
    combat_ratio: Literal["low", "medium", "high"] = "low"
    investigation_ratio: Literal["low", "medium", "high"] = "high"
```

---

## 4. 输出 contract

输出对象：

- `WorldSchema`
- `CharacterCreationProfile`
- `ModuleBlueprintSchema`

校验报告：

```python
class ModulePlayabilityReport(ValidationReport):
    missing_core_fields: list[str] = []
    uncovered_secret_ids: list[str] = []
    clue_path_count: int = 0
```

---

## 5. 核心 service

```python
class WorldGenerationService:
    async def generate(self, quick_start: QuickStartInput) -> WorldSchema: ...

class CharacterCreationProfileGenerationService:
    async def generate(self, world: WorldSchema) -> CharacterCreationProfile: ...

class ModuleGenerationService:
    async def generate(self, quick_start: QuickStartInput, world: WorldSchema) -> ModuleBlueprintSchema: ...

class ModulePlayabilityValidator:
    def validate(self, module: ModuleBlueprintSchema, world: WorldSchema) -> ModulePlayabilityReport: ...
```

要求：

1. 先生成 world，再根据 world 单独生成车卡规则，再生成 module。
2. 生成结果必须通过 schema 校验。
3. `fail` 时允许一次 repair pass。
4. world 生成阶段可用默认 `character_creation_profile` 兜底；正式角色审核前应运行车卡规则生成脚本。
5. 生成出的世界必须给出 `special_status_catalog`，可以为空，但字段必须存在。
6. 生成出的模组必须明确 `player_count_min` / `player_count_max`，供后续房间角色审核使用。

---

## 6. 建议脚本

1. `scripts/phase1/generate_world_draft.py`
2. `scripts/phase1/generate_character_creation_profile.py`
3. `scripts/phase1/generate_module_draft.py`
4. `scripts/phase1/validate_module_playability.py`

示例：

```bash
uv run python scripts/phase1/generate_world_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --output artifacts/worlds/rainy_town_world.json

uv run python scripts/phase1/generate_character_creation_profile.py \
  --world artifacts/worlds/rainy_town_world.json \
  --output artifacts/worlds/rainy_town_character_profile.json \
  --merged-world-output artifacts/worlds/rainy_town_world_with_profile.json
```

---

## 7. LLM 输出要求

1. 必须返回严格 JSON
2. 字段名与 schema 对齐
3. 不允许额外字段
4. 核心秘密、线索、结局必须显式存在
5. 世界生成 prompt 不要求一次性完成技能表；技能表由车卡规则生成 prompt 单独完成。
6. 车卡规则生成必须显式给出：
   - 基础属性定义
   - 属性取值范围
   - 属性分段语义说明
   - 技能列表
   - 技能点总量
   - 技能值 `0/1/2` 的语义说明

---

## 8. 产出

- `artifacts/worlds/<case_id>.json`
- `artifacts/worlds/<case_id>_character_profile.json`
- `artifacts/modules/<case_id>.json`
- `artifacts/evals/module_validation_<case_id>.json`

---

## 9. 测试要求

至少准备 10 组快速开团输入，覆盖中式怪谈、都市异闻、武侠悬疑、仙侠秘闻、无限流。

检查：

1. 世界结构完整
2. 模组结构完整
3. 模组包含核心秘密
4. 至少 3 条关键线索指向真相
5. 至少有好 / 中 / 差三个结局层级
6. 世界包含可消费的车卡规范
7. 模组人数范围与快速开团输入人数兼容

---

## 10. 完成标准

1. 10 组输入里至少 9 组生成结构完整 world/module
2. 至少 80% 模组满足“3 条关键线索指向真相”
3. 校验器可输出 `pass/warn/fail`
4. 车卡规则脚本输出可被角色审核链路直接消费的 `character_creation_profile`
