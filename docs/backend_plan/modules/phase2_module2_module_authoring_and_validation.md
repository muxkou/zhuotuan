# 阶段二 模块二：模组创作向导与深度校验

## 1. 模块目标

在阶段一快速生成的基础上，支持更细粒度的用户自定义模组创作和深度校验。

---

## 2. 建议代码落点

```text
backend/app/application/services/module_authoring_service.py
backend/app/application/validators/module_graph_validator.py
backend/app/application/validators/npc_consistency_validator.py
backend/app/application/validators/ending_validator.py
```

---

## 3. 输入 contract

```python
class ModuleWizardInput(BaseModel):
    world_id: str
    name: str
    opening_hook: str
    core_secret: str
    major_conflict: str
    required_npcs: list[dict]
    key_locations: list[dict]
    key_clues: list[dict]
    threat_clock: dict
    endings: dict[str, str]
    ai_freedom_level: Literal["conservative", "standard", "high"]
    ai_do_not_change: list[str]
```

---

## 4. 输出 contract

输出：

- `ModuleBlueprintSchema`
- 线索图校验报告
- NPC 一致性校验报告
- 结局完整性校验报告

---

## 5. 建议脚本

1. `scripts/phase2/create_module_blueprint.py`
2. `scripts/phase2/revise_module_blueprint.py`
3. `scripts/phase2/validate_module_graph.py`
4. `scripts/eval/eval_module_authoring_quality.py`

---

## 6. 深度校验重点

1. 线索图是否存在断路
2. 关键真相是否存在至少三条到达路径
3. NPC 动机与公开身份是否冲突
4. 倒计时是否可推进
5. 结局条件是否互斥且可判定

---

## 7. 完成标准

1. 用户显式填写内容可整合为完整模组
2. 能识别无解线索图、矛盾动机、空结局条件
3. 单模组深度校验 P95 < 15s
