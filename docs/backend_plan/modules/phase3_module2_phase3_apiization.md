# 阶段三 模块二：KP 副驾驶 API 化

## 1. 模块目标

将人类 KP 副驾驶脚本能力封装为 API，供传统带团流程调用。

---

## 2. 建议 API

1. `POST /v1/kp/npc-lines:suggest`
2. `POST /v1/kp/clues:remind`
3. `POST /v1/kp/actions:review`
4. `POST /v1/kp/reports:generate`

---

## 3. 契约要求

1. 所有 KP API 默认返回隐藏信息
2. 必须有权限隔离设计，不能给玩家直接访问

---

## 4. 完成标准

1. KP 副驾驶能力具备稳定 API
2. 与短团闭环能力共享统一状态模型
3. 不暴露不该给玩家看的隐藏信息
