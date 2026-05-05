import argparse
import json
from pathlib import Path

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.application.services.manual_character_card_service import (
    ManualCharacterCardService,
)
from backend.app.domain.schemas.character import ManualCharacterCardInput
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import CharacterCreationProfile, WorldSchema


def _load_world_with_profile(world_path: Path, profile_path: Path | None) -> WorldSchema:
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    if profile_path is None:
        return world
    profile = CharacterCreationProfile.model_validate(
        json.loads(profile_path.read_text(encoding="utf-8"))
    )
    return world.model_copy(update={"character_creation_profile": profile})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--character-output", type=Path)
    args = parser.parse_args()

    world = _load_world_with_profile(args.world, args.profile)
    module = ModuleBlueprintSchema.model_validate(
        json.loads(args.module.read_text(encoding="utf-8"))
    )
    ruleset = RuleSetSchema.model_validate(json.loads(args.ruleset.read_text(encoding="utf-8")))
    manual_input = ManualCharacterCardInput.model_validate(
        json.loads(args.input.read_text(encoding="utf-8"))
    )

    character = ManualCharacterCardService().build_character(manual_input, world)
    report = CharacterReviewPipeline().review(character, world, module, ruleset)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    if args.character_output is not None:
        args.character_output.parent.mkdir(parents=True, exist_ok=True)
        args.character_output.write_text(character.model_dump_json(indent=2), encoding="utf-8")
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
