import argparse
import asyncio
import json
from pathlib import Path
from statistics import mean
from time import perf_counter

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.domain.schemas.generation import CharacterQuestionnaire
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


async def _main(
    questionnaire_path: Path,
    world_path: Path,
    module_path: Path,
    ruleset_path: Path,
    runs: int,
    output_path: Path,
) -> None:
    questionnaire = CharacterQuestionnaire.model_validate(
        json.loads(questionnaire_path.read_text(encoding="utf-8"))
    )
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    module = ModuleBlueprintSchema.model_validate(
        json.loads(module_path.read_text(encoding="utf-8"))
    )
    ruleset = RuleSetSchema.model_validate(json.loads(ruleset_path.read_text(encoding="utf-8")))
    pipeline = CharacterReviewPipeline()

    latencies: list[float] = []
    for _ in range(runs):
        started_at = perf_counter()
        await pipeline.run(questionnaire, world, module, ruleset, allow_repair=True)
        latencies.append(round((perf_counter() - started_at) * 1000, 3))

    summary = {
        "case_id": questionnaire.case_id,
        "player_id": questionnaire.player_id,
        "runs": runs,
        "avg_ms": round(mean(latencies), 3),
        "max_ms": max(latencies),
        "min_ms": min(latencies),
        "samples_ms": latencies,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questionnaire", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
    )
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(
        _main(
            questionnaire_path=args.questionnaire,
            world_path=args.world,
            module_path=args.module,
            ruleset_path=args.ruleset,
            runs=args.runs,
            output_path=args.output,
        )
    )


if __name__ == "__main__":
    main()
