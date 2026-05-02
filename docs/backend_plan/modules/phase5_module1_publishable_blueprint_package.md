# 阶段五 模块一：可发布模组蓝图包

## 1. 模块目标

把可运行模组整理成可发布、可版本化、可复检的内容包格式。

---

## 2. 包结构建议

```text
package/
  manifest.json
  world.json
  module.json
  cover.md
  changelog.md
```

`manifest.json` 至少包含：

- package_id
- version
- world_version
- module_version
- schema_version
- author
- tags
- content_rating

---

## 3. 建议脚本

1. `scripts/phase5/build_blueprint_package.py`
2. `scripts/phase5/validate_publishable_package.py`
3. `scripts/eval/eval_package_compatibility.py`

---

## 4. 完成标准

1. 模组已具备标准化分发格式
2. 包可被系统重新导入
3. 发布前能发现缺失字段和非法内容
