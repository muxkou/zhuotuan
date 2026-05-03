import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.generation import CharacterQuestionnaire
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


async def _main(
    questionnaires_dir: Path,
    world_path: Path,
    module_path: Path,
    ruleset_path: Path,
    output_path: Path,
    max_cases: int | None,
) -> None:
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    module = ModuleBlueprintSchema.model_validate(
        json.loads(module_path.read_text(encoding="utf-8"))
    )
    ruleset = RuleSetSchema.model_validate(json.loads(ruleset_path.read_text(encoding="utf-8")))
    pipeline = CharacterReviewPipeline()

    case_paths = sorted(questionnaires_dir.glob("*_questionnaire.json"))
    if max_cases is not None:
        case_paths = case_paths[:max_cases]

    results: list[dict] = []
    for path in case_paths:
        questionnaire = CharacterQuestionnaire.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        started_at = perf_counter()
        try:
            run_output = await pipeline.run(
                questionnaire,
                world,
                module,
                ruleset,
                allow_repair=True,
            )
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
            results.append(
                {
                    "case_id": questionnaire.case_id,
                    "player_id": questionnaire.player_id,
                    "status": run_output.final_review_report.status,
                    "review_result": run_output.final_review_report.review_result,
                    "repair_attempted": run_output.repair_attempted,
                    "repaired": run_output.repaired,
                    "elapsed_ms": elapsed_ms,
                }
            )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
            results.append(
                {
                    "case_id": path.stem,
                    "status": ValidationStatus.FAIL,
                    "review_result": "needs_revision",
                    "repair_attempted": False,
                    "repaired": False,
                    "elapsed_ms": elapsed_ms,
                    "error": str(exc),
                }
            )

    summary = {
        "total_cases": len(results),
        "approved_like_count": sum(
            1
            for item in results
            if item["review_result"] in {"approved", "enhance"}
        ),
        "warning_count": sum(1 for item in results if item["review_result"] == "warning"),
        "needs_revision_count": sum(
            1 for item in results if item["review_result"] == "needs_revision"
        ),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--questionnaires-dir",
        type=Path,
        default=Path("artifacts/characters"),
    )
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/evals/character_batch_summary.json"),
    )
    parser.add_argument("--max-cases", type=int, default=None)
    args = parser.parse_args()
    asyncio.run(
        _main(
            questionnaires_dir=args.questionnaires_dir,
            world_path=args.world,
            module_path=args.module,
            ruleset_path=args.ruleset,
            output_path=args.output,
            max_cases=args.max_cases,
        )
    )


if __name__ == "__main__":
    main()
