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

根据 world 单独生成车卡规则：

```bash
uv run python scripts/phase1/generate_character_creation_profile.py \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --output artifacts/worlds/quickstart_rainy_town_character_profile.json \
  --merged-world-output artifacts/worlds/quickstart_rainy_town_with_profile.json
```

单 case 生成 module：

```bash
uv run python scripts/phase1/generate_module_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --output artifacts/modules/quickstart_rainy_town.json
```

如果 repair pass 请求模型超时，先拉长 `.env` 中的 `LLM_TIMEOUT_SECONDS`，或临时禁用 repair 只观察初稿：

```bash
uv run python scripts/phase1/generate_module_draft.py \
  --input artifacts/cases/quickstart_rainy_town.json \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --output artifacts/modules/quickstart_rainy_town.json \
  --no-repair
```

校验单 case 模组可运行性：

```bash
uv run python scripts/phase1/validate_module_playability.py \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/evals/module_validation_quickstart_rainy_town.json
```

### Phase 1 Module 3

单 case 生成角色草案：

```bash
uv run python scripts/phase1/generate_character_draft.py \
  --questionnaire artifacts/characters/quickstart_rainy_town_questionnaire.json \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_draft.json
```

审核角色草案：

```bash
uv run python scripts/phase1/review_character_sheet.py \
  --input artifacts/characters/quickstart_rainy_town_draft.json \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_review.json
```

审核玩家手动填写的车卡：

```bash
uv run python scripts/phase1/review_manual_character_card.py \
  --input artifacts/characters/quickstart_rainy_town_manual_card.json \
  --world artifacts/worlds/quickstart_rainy_town.json \
  --profile artifacts/worlds/quickstart_rainy_town_character_profile.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_manual_review.json \
  --character-output artifacts/characters/quickstart_rainy_town_manual_character.json
```

顺序审核一个房间内的多张角色草案：

```bash
uv run python scripts/phase1/review_character_roster_queue.py \
  --characters-dir artifacts/characters \
  --world artifacts/worlds/quickstart_rainy_town_with_profile.json \
  --module artifacts/modules/quickstart_rainy_town.json \
  --output artifacts/characters/quickstart_rainy_town_roster_review.json
```

当前阶段角色审核新增关注点：

- world 可以先生成基础草案，再通过车卡规则脚本补 `character_creation_profile`
- world 中必须带 `special_status_catalog`
- character 会同时受轻规则必填项和 world 车卡约束检查
- 技能必须来自世界技能表，值只能是 `0/1/2`，总点数不能超过世界技能点预算
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
