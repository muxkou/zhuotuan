# 桌团后端开发统一约定

## 1. 使用方式

`docs/backend_plan/modules/` 下的所有模块文档默认继承本文约定。把模块文档交给 Codex 前，先让它阅读本文。

---

## 2. 统一目录建议

```text
backend/
  app/
    domain/
      enums/
      schemas/
      value_objects/
    application/
      services/
      validators/
      orchestrators/
    infra/
      llm/
      storage/
      telemetry/
    api/
      routers/
  scripts/
    phase1/
    phase2/
    phase3/
    phase4/
    phase5/
    eval/
    perf/
    replay/
  tests/
    unit/
    integration/
    golden/
  artifacts/
```

---

## 3. 统一 schema 规则

1. 外部输入输出一律使用 Pydantic v2。
2. 所有 artifact 对象建议包含：
   - `id`
   - `version`
   - `created_at`
   - `source`
3. 所有 LLM 产物先进入 `draft schema`，校验通过后再转成 `validated schema`。
4. 运行时状态必须和静态蓝图分离。

建议 artifact 包装结构：

```json
{
  "meta": {
    "artifact_type": "world|module|character|session|report|eval",
    "schema_version": "v1",
    "generated_by": "script_name",
    "case_id": "case_demo_001"
  },
  "data": {}
}
```

---

## 4. 统一错误与校验报告

```python
class ErrorItem(BaseModel):
    code: str
    message: str
    field_path: str | None = None
    severity: Literal["info", "warning", "error"]
    suggestion: str | None = None

class ValidationReport(BaseModel):
    status: Literal["pass", "warn", "fail"]
    hard_errors: list[ErrorItem] = []
    warnings: list[ErrorItem] = []
    suggestions: list[str] = []
    metrics: dict[str, float | int | str] = {}
```

---

## 5. 统一脚本 CLI 约定

所有脚本尽量支持：

```text
--input <path>
--output <path>
--case-id <str>
--config <path>
--model <str>
--max-retries <int>
--pretty
```

退出码建议：

- `0`：成功
- `1`：输入错误
- `2`：LLM / 网络失败
- `3`：schema 失败
- `4`：业务校验失败

---

## 6. 统一测试要求

每个模块至少有三类测试：

1. `unit`
2. `integration`
3. `golden`

---

## 7. API 化约定

API 只能包装已经通过脚本验证的能力。FastAPI 路由尽量薄，只做：

1. 参数接收
2. 调用 service
3. 返回 schema
4. 打日志与 trace
