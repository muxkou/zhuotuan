import argparse
import json
from pathlib import Path

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characters-dir", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    world = WorldSchema.model_validate(json.loads(args.world.read_text(encoding="utf-8")))
    module = ModuleBlueprintSchema.model_validate(
        json.loads(args.module.read_text(encoding="utf-8"))
    )
    ruleset = RuleSetSchema.model_validate(json.loads(args.ruleset.read_text(encoding="utf-8")))
    character_paths = sorted(args.characters_dir.glob("*_draft.json"))

    pipeline = CharacterReviewPipeline()
    approved_characters: list[CharacterSheetSchema] = []
    results: list[dict] = []

    for index, path in enumerate(character_paths, start=1):
        character = CharacterSheetSchema.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        report = pipeline.review(
            character,
            world,
            module,
            ruleset,
            existing_characters=approved_characters,
            queue_position=index,
        )
        results.append(
            {
                "file": str(path),
                "character_id": character.id,
                "status": report.status,
                "review_result": report.review_result,
                "queue_position": report.queue_position,
                "roster_conflicts": report.roster_conflicts,
                "blocking_reasons": report.blocking_reasons,
            }
        )
        if report.status == ValidationStatus.PASS:
            approved_characters.append(character)

    summary = {
        "total_characters": len(character_paths),
        "approved_count": len(approved_characters),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
