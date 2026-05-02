# 桌团后端技术方案设计

## 1. 文档目标

本文基于 `docs/zhuotuan_product_design.md`，只讨论后端方案，不包含前端设计与具体编码实现。目标是把产品 PRD 转换为：

- 可验证的后端技术路线；
- 以脚本实验优先的研发节奏；
- 以 FastAPI 为最终业务承载层的落地方案；
- 以 `uv` 为开发环境基础的工程约束；
- 可按阶段递进实现和验收的开发计划。

当前原则：

1. 不直接先做 API，先做脚本验证。
2. 先验证可行性、性能、效果，再把稳定能力 API 化。
3. 不使用 agent 框架，只用代码逻辑串联 LLM API。
4. 所有方案优先服务后端闭环。

---

## 2. 产品到后端的核心映射

PRD 的核心不是“AI 即兴讲故事”，而是“受约束的动态模组运行器”。因此后端的核心职责应为：

1. 管理结构化规则、世界、模组、跑团实例、会话状态。
2. 调用 LLM 执行有限职责，而不是把整场游戏交给单次自由对话。
3. 通过状态机、约束检查和结构化产物锁定真相、线索、公平性和连续性。
4. 通过可回放的脚本和 JSON 产物先验证每一段流程。

后端领域对象建议严格对应 PRD 五层结构：

- `RuleSet`
- `World`
- `ModuleBlueprint`
- `TableInstance`
- `Session`

并补充运行时对象：

- `CharacterSheet`
- `NpcState`
- `ClueState`
- `ThreatClock`
- `TurnRecord`
- `SessionReport`
- `EvaluationCase`

---

## 3. 总体架构

### 3.1 分层

建议后端按五层组织：

1. `domain`
   - 规则、世界、模组、房间、角色、线索、NPC、倒计时等领域模型
2. `application`
   - 建模校验、流程编排、回合推进、战报生成、评测任务
3. `infra`
   - LLM client、文件存储、JSON artifact、数据库、日志、缓存
4. `scripts`
   - 可复现实验脚本、离线评测脚本、性能压测脚本
5. `api`
   - FastAPI 路由，仅包装已验证稳定的能力

### 3.2 LLM 使用原则

LLM 不直接拥有“游戏主权”，只负责以下明确任务：

1. 生成草案：
   - 世界草案
   - 模组草案
   - 角色卡草案
2. 结构化校验：
   - 字段完整性
   - 动机合理性
   - 线索覆盖度
3. 运行时演出：
   - 场景叙述
   - NPC 对话
   - 后果表述
4. 文本总结：
   - Session 0 摘要
   - 战报
   - 风险提示

最终约束必须由后端代码保证：

1. 核心秘密不可被 LLM 自改。
2. 关键线索不可丢失。
3. 掷骰与难度不可黑箱变更。
4. 已公开信息必须可追溯。
5. 威胁倒计时推进逻辑必须代码可见。

### 3.3 数据与状态

研发顺序建议分两阶段：

1. 脚本阶段：
   - 以 YAML / JSON 文件为主
   - 不强依赖数据库
   - 产出实验 artifact，便于人工复盘
2. API 化阶段：
   - 再接入数据库持久化
   - 将稳定的 JSON schema 转成 ORM / repository

建议的中间产物目录：

- `artifacts/worlds/`
- `artifacts/modules/`
- `artifacts/characters/`
- `artifacts/sessions/`
- `artifacts/evals/`
- `artifacts/reports/`

---

## 4. 工程约束

### 4.1 技术栈

- Python 3.11+
- `uv`：环境、依赖、脚本入口管理
- FastAPI：最终 API 承载
- Pydantic v2：领域对象与输入输出 schema
- SQLAlchemy / SQLModel：API 化后的持久层
- httpx：LLM API 调用
- pytest：单元测试与流程回归
- Typer 或纯 Python 脚本：实验入口

### 4.2 明确不做

- 不使用 LangChain、LangGraph、AutoGen 一类 agent 框架
- 不做“全对话即状态”的黑盒实现
- 不以数据库先行为前提推进能力验证
- 不将 prompt 当作唯一逻辑层

### 4.3 推荐目录

```text
backend/
  app/
    api/
    application/
    domain/
    infra/
    prompts/
    services/
  scripts/
    phase1/
    phase2/
    eval/
    perf/
  tests/
  artifacts/
  pyproject.toml
```

---

## 5. 核心后端能力设计

### 5.1 规则与领域模型层

目标：把 PRD 中“世界 / 模组 / 角色 / 线索 / NPC / 倒计时 / 会话”先稳定成强约束 schema。

重点：

1. 先有结构，再谈文案。
2. 所有 LLM 输入输出都要绑定 schema。
3. 每个核心对象都要支持：
   - `draft`
   - `validated`
   - `runtime_snapshot`

建议关键 schema：

- `RuleSetSchema`
- `WorldSchema`
- `ModuleBlueprintSchema`
- `CharacterDraftSchema`
- `CharacterValidatedSchema`
- `NpcSchema`
- `ClueSchema`
- `ThreatClockSchema`
- `TurnResolutionSchema`
- `SessionSummarySchema`

### 5.2 世界与模组生成层

目标：根据快速开团输入或创作输入，生成“可运行而非只好看”的蓝图。

生成链路建议：

1. 输入题材、时长、氛围、灵感。
2. 生成世界草案。
3. 生成模组草案。
4. 运行结构校验。
5. 运行质量校验。
6. 若失败则再修补，不直接入库。
7. 导出 JSON 供人工审阅和后续脚本使用。

### 5.3 模组可运行性校验层

目标：把 PRD 第 10 章变成代码可判定的检查器。

建议拆成两类：

1. 硬校验：
   - 核心秘密是否存在
   - 必要 NPC 是否存在
   - 关键地点是否存在
   - 结局条件是否完整
   - AI 禁止事项是否存在
2. 软校验：
   - 是否至少 3 条线索指向关键真相
   - 关键线索是否有替代路径
   - 玩家开局动机是否明确
   - NPC 动机是否自洽
   - 威胁倒计时是否形成推进链

输出应为结构化报告：

```json
{
  "status": "pass|warn|fail",
  "hard_errors": [],
  "soft_warnings": [],
  "repair_suggestions": [],
  "scores": {
    "clue_coverage": 0.0,
    "npc_consistency": 0.0,
    "ending_judgeability": 0.0
  }
}
```

### 5.4 角色创建与审核层

目标：先验证角色生成与审核链路是否稳定，再 API 化。

链路建议：

1. 玩家回答问卷。
2. LLM 生成角色草案。
3. 规则检查器验证点数和字段。
4. 世界观检查器验证设定边界。
5. 模组适配检查器验证动机和剧透风险。
6. 输出审核结论与修改建议。

### 5.5 Session 0 编排层

目标：把玩家角色与模组钩子绑定，并生成本桌公开信息与边界约束。

输出应至少包含：

- 房间风格确认
- 边界确认
- 角色关系表
- 角色开局动机
- 公共开场摘要
- 每名角色隐藏钩子

### 5.6 正式游玩编排层

目标：将“玩家输入 -> 意图识别 -> 是否判定 -> 结果描述 -> 状态更新”变为确定性流程。

后端必须显式拆分以下步骤：

1. `parse_player_action`
2. `classify_intent`
3. `decide_roll_needed`
4. `compute_difficulty`
5. `resolve_roll`
6. `compose_consequence`
7. `update_runtime_state`
8. `emit_turn_record`

其中：

- 骰点、修正、难度、结果等级由代码计算；
- LLM 只负责意图补充、叙事包装和备选方案表述；
- 运行态必须生成 `TurnRecord` JSON。

### 5.7 线索、NPC、倒计时状态层

目标：将 PRD 中最容易“AI 忘记”的部分全部外部化为状态。

关键要求：

1. 线索板由代码控制状态迁移。
2. NPC 有可见态和隐藏态。
3. 倒计时推进必须由触发器驱动。
4. 每次回合结算后产出新的状态快照。

### 5.8 战报与复盘层

目标：把长会话压缩成可继续下一场的稳定结构。

输入：

- 全量回合记录
- 状态前后差异
- 关键骰点记录

输出：

- 本场摘要
- 重要事件
- 线索新增
- 未解决问题
- 角色状态变化
- NPC 状态变化
- 倒计时变化
- 下场建议

---

## 6. 研发策略：先脚本，后 API

### 6.1 为什么必须先脚本

这个项目早期风险不在“HTTP 接口会不会写”，而在以下问题：

1. 世界和模组生成是否稳定可玩；
2. 校验器能否识别无解模组；
3. 角色审核会不会过严或过松；
4. 回合编排是否会出现状态漂移；
5. LLM 成本、延迟、失败率是否可接受；
6. 战报是否真正能帮助下一场继续。

这些问题更适合通过脚本和离线数据先验证。

### 6.2 脚本优先研发模式

每个模块都遵循统一流程：

1. 写领域 schema
2. 写离线脚本
3. 输入固定样例
4. 导出 JSON artifact
5. 人工复盘结果质量
6. 运行回归脚本
7. 通过后再进入 API 化

### 6.3 脚本类型

建议至少有四类脚本：

1. `demo` 脚本
   - 演示单条流程跑通
2. `eval` 脚本
   - 批量案例验证效果
3. `perf` 脚本
   - 并发、延迟、token、成本统计
4. `replay` 脚本
   - 复现历史 artifact，确保行为稳定

---

## 7. 性能、效果与可行性指标

### 7.1 可行性指标

用于回答“这段能力能不能做”：

1. 结构化输出成功率
2. 单次重试后成功率
3. 跨 20 组样例的一致性
4. 对坏输入的修复能力
5. 人工审阅通过率

### 7.2 效果指标

用于回答“做出来好不好用”：

1. 模组校验误判率
2. 角色审核建议可接受率
3. 线索推进可玩率
4. 战报信息遗漏率
5. 结局判断一致性

### 7.3 性能指标

用于回答“能不能承载真实业务”：

1. 每个脚本任务平均耗时
2. P95 耗时
3. 每任务平均 token 消耗
4. 每任务平均成本
5. 并发 5 / 10 / 20 下错误率

### 7.4 第一阶段建议门槛

建议在进入 API 化前，单模块至少达到：

1. 结构化输出成功率 >= 90%
2. 重试一次后成功率 >= 97%
3. 单次任务 P95 < 15s
4. 关键状态字段遗漏率 < 5%
5. 至少 10 个固定样例可稳定复现

---

## 8. API 化原则

当某一模块脚本验证稳定后，再封装 API。API 层职责应尽量薄：

1. 接收请求
2. 调用已验证的 application service
3. 记录任务状态
4. 返回结构化结果

API 不是验证逻辑本体，只是承载层。

### 8.1 推荐首批 API

当阶段一脚本验证完成后，可优先提供：

- `POST /v1/worlds/draft:generate`
- `POST /v1/modules/draft:generate`
- `POST /v1/modules/validate`
- `POST /v1/characters/draft:generate`
- `POST /v1/characters/review`
- `POST /v1/session-zero/prepare`
- `POST /v1/tables/{table_id}/turns:resolve`
- `POST /v1/sessions/{session_id}/report:generate`

### 8.2 API 化前置条件

每个 API 对应能力必须先满足：

1. 有固定 schema
2. 有脚本演示
3. 有 eval 样例集
4. 有 perf 结果
5. 有失败与重试策略

---

## 9. 阶段性交付策略

按 PRD 路线图，后端建议分五个阶段推进：

1. 阶段一：AI KP 短团闭环
2. 阶段二：自定义世界与模组
3. 阶段三：人类 KP 副驾驶
4. 阶段四：多人在线体验增强
5. 阶段五：创作者生态

但每个阶段内部继续拆成“可独立验证模块”，并坚持：

1. 先 schema
2. 再脚本
3. 再评测
4. 最后 API

详细计划见：

- `docs/backend_plan/README.md`

---

## 10. 技术风险与应对

### 10.1 LLM 输出不稳定

应对：

1. 严格 schema 验证
2. 分步提示，不做大而全 prompt
3. 增加 repair pass
4. 所有关键产物落盘可复盘

### 10.2 状态漂移

应对：

1. 回合后强制状态快照
2. LLM 不直接修改主状态
3. 用事件流更新线索、NPC、倒计时

### 10.3 成本过高

应对：

1. 将长链路拆分为小任务
2. 只对必要部分调用 LLM
3. 战报与评测离线批处理
4. 对固定 schema 结果做缓存

### 10.4 API 过早固化

应对：

1. 先脚本和 artifact
2. 用评测结果筛掉不稳定接口
3. 将 API 放到阶段后置

---

## 11. 结论

这个项目的后端正确切入点，不是先做“聊天接口”，而是先做“结构化跑团引擎”：

1. 用 schema 锁定规则、世界、模组和运行态；
2. 用脚本验证 LLM 在生成、校验、主持、总结各环节的可行性；
3. 用 JSON artifact 代替早期数据库依赖；
4. 用评测和性能数据决定何时 API 化；
5. 最终由 FastAPI 承载经过验证的稳定能力。

如果按这个顺序推进，后端可以在不引入 agent 框架的前提下，逐步完成 PRD 所需的 AI KP 闭环。
