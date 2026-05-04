# Zhuotuan Backend

FastAPI backend scaffold for the Zhuotuan AI TRPG platform.

## Quick Start

```bash
uv sync
uv run zhuotuan dev
```

## Validation And Test Commands

### Base Checks

代码风格检查：

```bash
uv run ruff check backend scripts tests
```

运行全部测试：

```bash
uv run pytest tests/unit tests/integration tests/golden
```

做一次 Python 编译检查：

```bash
PYTHONPYCACHEPREFIX=/tmp/zhuotuan_pycache python3 -m compileall backend tests scripts
```

### Phase 1 Module 1

重新生成最小样例 artifact：

```bash
uv run python scripts/phase1/build_minimum_schemas.py
```

校验最小样例 artifact：

```bash
uv run python scripts/phase1/validate_sample_assets.py \
  --input artifacts \
  --output artifacts/evals/schema_report.json
```

运行 schema 回归脚本：

```bash
uv run python scripts/eval/schema_regression.py
```

### Phase 1 Module 2

单 case 生成 world：

```bash
uv run python scripts/phase1/generate_world_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --output artifacts/worlds/quickstart_rainy_town.json
```

单 case 生成 module：

```bash
uv run python scripts/phase1/generate_module_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --output artifacts/modules/quickstart_rainy_town.json
```

校验单 case 模组可运行性：

```bash
uv run python scripts/phase1/validate_module_playability.py \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/evals/module_validation_quickstart_rainy_town.json
```

批量评测 world + module 生成链路：

```bash
uv run python scripts/eval/eval_world_module_batch.py \
  --cases-dir artifacts/cases \
  --output artifacts/evals/world_module_batch_summary.json \
  --max-cases 2
```

性能采样：

```bash
uv run python scripts/perf/perf_world_module_generation.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --runs 3 \
  --output artifacts/evals/perf_rainy_town.json
```

### Phase 1 Module 3

单 case 生成角色草案：

```bash
uv run python scripts/phase1/generate_character_draft.py \
  --questionnaire artifacts/characters/quickstart_rainy_town_questionnaire.json \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_draft.json
```

审核角色草案：

```bash
uv run python scripts/phase1/review_character_sheet.py \
  --input artifacts/characters/quickstart_rainy_town_draft.json \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_review.json
```

顺序审核一个房间内的多张角色草案：

```bash
uv run python scripts/phase1/review_character_roster_queue.py \
  --characters-dir artifacts/characters \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_roster_review.json
```

批量评测角色生成与审核链路：

```bash
uv run python scripts/eval/eval_character_review.py \
  --questionnaires-dir artifacts/characters \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/evals/character_batch_summary.json \
  --max-cases 1
```

角色链路性能采样：

```bash
uv run python scripts/perf/perf_character_pipeline.py \
  --questionnaire artifacts/characters/quickstart_rainy_town_questionnaire.json \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --runs 3 \
  --output artifacts/evals/perf_character_rainy_town.json
```

### Phase 1 End-to-End Flow

运行当前阶段一全流程脚本：

```bash
uv run python scripts/phase1/run_quickstart_flow.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --output-dir artifacts/runs
```

带角色问卷运行到 character 阶段：

```bash
uv run python scripts/phase1/run_quickstart_flow.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --questionnaire artifacts/characters/quickstart_rainy_town_questionnaire.json \
  --output-dir artifacts/runs
```

禁用 repair pass 做对照：

```bash
uv run python scripts/phase1/run_quickstart_flow.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --output-dir artifacts/runs \
  --no-repair
```

全流程脚本当前会输出：

- `artifacts/runs/<case_id>/quick_start_input.json`
- `artifacts/runs/<case_id>/world.json`
- `artifacts/runs/<case_id>/world_raw_response.txt`
- `artifacts/runs/<case_id>/module.json`
- `artifacts/runs/<case_id>/module_generation_report.json`
- `artifacts/runs/<case_id>/module_initial_raw_response.txt`
- `artifacts/runs/<case_id>/module_repair_raw_response.txt`
- `artifacts/runs/<case_id>/character_questionnaire.json`
- `artifacts/runs/<case_id>/character.json`
- `artifacts/runs/<case_id>/character_generation_report.json`
- `artifacts/runs/<case_id>/character_initial_raw_response.txt`
- `artifacts/runs/<case_id>/character_repair_raw_response.txt`
- `artifacts/runs/<case_id>/flow_summary.json`

重点查看：

- `flow_summary.json`：看全流程耗时、最终状态、是否触发 repair
- `module_generation_report.json`：看 `initial_report` 和 `final_report` 的变化
- `character_generation_report.json`：看 `initial_review_report` 和 `final_review_report` 的变化

当前阶段角色审核新增关注点：

- world 中必须带 `character_creation_profile`
- world 中必须带 `special_status_catalog`
- character 会同时受轻规则预算和 world 车卡约束检查
- 同一房间内的角色可以通过队列脚本按顺序审核，后提交者会参考已通过角色

## Project Layout

```text
backend/
  app/
    api/
    application/
    domain/
    infra/
scripts/
tests/
artifacts/
docs/
```
