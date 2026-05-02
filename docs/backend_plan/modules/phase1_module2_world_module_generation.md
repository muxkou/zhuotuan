# 阶段一 模块二：世界与模组生成可行性验证

## 1. 模块目标

验证“快速开团输入 -> 世界草案 -> 模组草案 -> 校验结果”是否稳定可用。

本模块优先验证生成质量，不做 API。

---

## 2. 建议代码落点

```text
backend/app/application/services/world_generation_service.py
backend/app/application/services/module_generation_service.py
backend/app/application/validators/module_playability_validator.py
backend/app/infra/llm/llm_client.py
backend/app/prompts/world_generation.md
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

class ModuleGenerationService:
    async def generate(self, quick_start: QuickStartInput, world: WorldSchema) -> ModuleBlueprintSchema: ...

class ModulePlayabilityValidator:
    def validate(self, module: ModuleBlueprintSchema, world: WorldSchema) -> ModulePlayabilityReport: ...
```

要求：

1. 先生成 world，再生成 module。
2. 生成结果必须通过 schema 校验。
3. `fail` 时允许一次 repair pass。

---

## 6. 建议脚本

1. `scripts/phase1/generate_world_draft.py`
2. `scripts/phase1/generate_module_draft.py`
3. `scripts/phase1/validate_module_playability.py`
4. `scripts/eval/eval_world_module_batch.py`
5. `scripts/perf/perf_world_module_generation.py`

示例：

```bash
uv run python scripts/phase1/generate_world_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --output artifacts/worlds/rainy_town_world.json
```

---

## 7. LLM 输出要求

1. 必须返回严格 JSON
2. 字段名与 schema 对齐
3. 不允许额外字段
4. 核心秘密、线索、结局必须显式存在

---

## 8. 产出

- `artifacts/worlds/<case_id>.json`
- `artifacts/modules/<case_id>.json`
- `artifacts/evals/module_validation_<case_id>.json`
- `artifacts/evals/world_module_batch_summary.json`

---

## 9. 测试要求

至少准备 10 组快速开团输入，覆盖中式怪谈、都市异闻、武侠悬疑、仙侠秘闻、无限流。

检查：

1. 世界结构完整
2. 模组结构完整
3. 模组包含核心秘密
4. 至少 3 条关键线索指向真相
5. 至少有好 / 中 / 差三个结局层级

---

## 10. 完成标准

1. 10 组输入里至少 9 组生成结构完整 world/module
2. 至少 80% 模组满足“3 条关键线索指向真相”
3. 校验器可输出 `pass/warn/fail`
4. 单次完整链路 P95 < 12s
