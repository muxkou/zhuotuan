import argparse
import asyncio
import json
from pathlib import Path

from backend.app.application.services.character_generation_service import (
    CharacterGenerationService,
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

    result = await CharacterGenerationService().generate(questionnaire, world, module, ruleset)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.character.model_dump_json(indent=2), encoding="utf-8")
    if result.raw_text is not None:
        output_path.with_suffix(".raw.txt").write_text(result.raw_text, encoding="utf-8")


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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(
        _main(
            questionnaire_path=args.questionnaire,
            world_path=args.world,
            module_path=args.module,
            ruleset_path=args.ruleset,
            output_path=args.output,
        )
    )


if __name__ == "__main__":
    main()
