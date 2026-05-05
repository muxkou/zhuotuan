# 桌团后端开发计划总览

## 1. 计划目标

本目录按 `docs/zhuotuan_product_design.md` 的产品阶段组织，但每个阶段继续拆成可独立开发、独立校验、顺序推进的模块。所有模块遵循统一原则：

1. 先做脚本，不先做 API。
2. 先用单步骤脚本验证可行性和效果，再决定是否补性能专项。
3. 产出优先为 JSON / Markdown / 日志，不强制先入库。
4. 达到阈值后再封装为 FastAPI API。

---

## 2. 阶段与模块总表

### 阶段一：AI KP 短团闭环

1. `phase1_module1_domain_and_rules.md`
2. `phase1_module2_world_module_generation.md`
3. `phase1_module3_character_pipeline.md`
4. `phase1_module4_session0_preparation.md`
5. `phase1_module5_turn_orchestration.md`
6. `phase1_module6_runtime_state_and_report.md`
7. `phase1_module7_phase1_apiization.md`

### 阶段二：自定义世界与模组

1. `phase2_module1_world_authoring.md`
2. `phase2_module2_module_authoring_and_validation.md`
3. `phase2_module3_phase2_apiization.md`

### 阶段三：人类 KP 副驾驶

1. `phase3_module1_copilot_assist_scripts.md`
2. `phase3_module2_phase3_apiization.md`

### 阶段四：多人在线体验增强

1. `phase4_module1_realtime_state_contract.md`
2. `phase4_module2_private_info_and_ops.md`

### 阶段五：创作者生态

1. `phase5_module1_publishable_blueprint_package.md`
2. `phase5_module2_creator_distribution_api.md`

---

## 3. 顺序依赖

建议按以下主顺序开发：

1. 阶段一全部完成
2. 阶段二前两个模块完成
3. 再决定阶段二 API 化
4. 阶段三基于已有 artifact 和状态引擎扩展
5. 阶段四基于稳定 API 与状态快照扩展多人协同
6. 阶段五最后建设内容生态

其中关键依赖为：

- 阶段一模块 1 是所有后续模块前置
- 阶段一模块 3 依赖模块 1-2 中的世界车卡约束和模组人数范围
- 阶段一模块 4 依赖模块 3 输出的顺序审核结果与房间角色 roster
- 阶段一模块 5 依赖模块 1-4
- 阶段一模块 6 依赖模块 5
- 每个阶段的 API 化模块均依赖该阶段前置脚本模块

---

## 4. 统一验收门槛

所有模块默认要同时满足三类验收：

1. 可行性验收
   - 流程能稳定跑通
2. 效果验收
   - 输出对业务有价值
3. 稳定性验收
   - 结构化输出、重试、后处理和校验结果可接受

建议门槛：

- 结构化输出成功率 >= 90%
- 重试一次后成功率 >= 97%
- 固定样例集通过率 >= 85%

---

## 5. 模块文档位置

所有模块文档都在：

- `docs/backend_plan/modules/`
- `docs/backend_plan/development_conventions.md`

建议阅读顺序也按模块编号顺序进行。

如果希望直接交给 Codex 开发，建议顺序是：

1. 先读 `development_conventions.md`
2. 再读对应模块文档
3. 按模块文档中的 schema、脚本、测试和产出要求直接实施
