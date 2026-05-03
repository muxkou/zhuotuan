# 阶段二 模块一：世界编辑与复用后端能力

## 1. 模块目标

支持用户创建、修改、版本化复用世界定义，并保证编辑后的世界仍可被阶段一和阶段二后续能力消费。

---

## 2. 建议代码落点

```text
backend/app/application/services/world_authoring_service.py
backend/app/application/services/world_versioning_service.py
backend/app/application/validators/world_consistency_validator.py
```

---

## 3. 输入输出 contract

输入：

- 世界模板 JSON
- 世界编辑 patch

输出：

- `WorldSchema`
- `ValidationReport`
- 世界版本 diff 报告

世界编辑能力必须允许维护下列结构：

1. `character_creation_profile`
   - 基础属性定义
   - 世界特有属性定义
   - 属性语义区间说明
   - 车卡禁止项
2. `special_status_catalog`
   - 特殊状态
   - 行为约束
   - 恢复提示

---

## 4. 建议脚本

1. `scripts/phase2/create_world_from_template.py`
2. `scripts/phase2/revise_world_draft.py`
3. `scripts/phase2/diff_world_versions.py`
4. `scripts/eval/eval_world_reusability.py`

---

## 5. 产出

- 可复用 `world package` JSON
- 世界版本差异报告
- 世界规则一致性报告

---

## 6. 完成标准

1. 世界具备版本化和复用能力
2. 同一世界可支撑多个模组草案生成
3. 世界编辑后仍可直接供角色审核链路消费
4. 世界编辑与重校验 P95 < 10s
