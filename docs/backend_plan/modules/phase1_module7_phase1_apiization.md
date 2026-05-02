# 阶段一 模块七：短团闭环 API 化

## 1. 模块目标

在前六个脚本模块稳定后，将阶段一核心能力封装为 FastAPI API。

---

## 2. 前置条件

必须先满足：

1. 世界 / 模组 / 角色 / Session 0 / 回合 / 战报全部已有脚本版
2. 已有固定 schema
3. 已有 eval 样例
4. 已有 perf 数据

---

## 3. 建议 API

1. `POST /v1/worlds/draft:generate`
2. `POST /v1/modules/draft:generate`
3. `POST /v1/modules/validate`
4. `POST /v1/characters/draft:generate`
5. `POST /v1/characters/review`
6. `POST /v1/session-zero/prepare`
7. `POST /v1/tables/{table_id}/turns:resolve`
8. `POST /v1/sessions/{session_id}/report:generate`

---

## 4. API contract 示例

### `POST /v1/modules/validate`

request:

```json
{
  "world_id": "world_tanxi_001",
  "module_id": "module_rainy_house_001"
}
```

response:

```json
{
  "status": "warn",
  "hard_errors": [],
  "warnings": [],
  "suggestions": ["增加一条可替代线索"],
  "metrics": {
    "clue_path_count": 2
  }
}
```

### `POST /v1/tables/{table_id}/turns:resolve`

request:

```json
{
  "session_id": "sess_001",
  "actor_id": "player_chenyan",
  "player_text": "我去祠堂后门看看有没有脚印"
}
```

response:

```json
{
  "turn_record": {},
  "player_visible_updates": {},
  "hidden_updates": {}
}
```

---

## 5. 实现要求

1. API 内部直接调用对应 service，不复制业务逻辑
2. 所有接口写契约测试
3. 所有接口都记录 `request_id`

---

## 6. 产出

1. FastAPI 路由定义文档
2. OpenAPI schema
3. API 契约测试
4. 脚本到 API 一致性报告

---

## 7. 完成标准

1. 阶段一能力已有稳定 API 入口
2. API 返回结构与脚本输出一致
3. 仍可通过 artifact 回放定位问题
