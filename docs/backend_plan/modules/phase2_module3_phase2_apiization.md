# 阶段二 模块三：世界与模组编辑 API 化

## 1. 模块目标

将阶段二的世界编辑和模组创作能力封装为 FastAPI 服务。

---

## 2. 建议 API

1. `POST /v1/worlds`
2. `PATCH /v1/worlds/{world_id}`
3. `GET /v1/worlds/{world_id}/versions`
4. `POST /v1/modules`
5. `PATCH /v1/modules/{module_id}`
6. `POST /v1/modules/{module_id}:validate`

---

## 3. 契约要求

1. 世界编辑接口支持幂等更新
2. 模组编辑接口支持部分 patch
3. 校验接口返回结构与脚本版一致

---

## 4. 完成标准

1. 自定义世界和模组可通过 API 操作
2. 阶段一短团引擎可直接消费阶段二产物
3. API 结果与脚本结果一致
