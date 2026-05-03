import argparse
import json
from pathlib import Path

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    character = CharacterSheetSchema.model_validate(
        json.loads(args.input.read_text(encoding="utf-8"))
    )
    world = WorldSchema.model_validate(json.loads(args.world.read_text(encoding="utf-8")))
    module = ModuleBlueprintSchema.model_validate(
        json.loads(args.module.read_text(encoding="utf-8"))
    )
    ruleset = RuleSetSchema.model_validate(json.loads(args.ruleset.read_text(encoding="utf-8")))

    report = CharacterReviewPipeline().review(character, world, module, ruleset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
