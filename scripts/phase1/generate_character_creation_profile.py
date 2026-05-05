import argparse
import asyncio
import json
from pathlib import Path

from backend.app.application.services.character_creation_profile_generation_service import (
    CharacterCreationProfileGenerationService,
)
from backend.app.domain.schemas.world import WorldSchema


async def _main(world_path: Path, output_path: Path, merged_world_output: Path | None) -> None:
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    service = CharacterCreationProfileGenerationService()
    result = await service.generate(world)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.profile.model_dump_json(indent=2), encoding="utf-8")
    if merged_world_output is not None:
        merged_world = world.model_copy(update={"character_creation_profile": result.profile})
        merged_world_output.parent.mkdir(parents=True, exist_ok=True)
        merged_world_output.write_text(merged_world.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--merged-world-output", type=Path)
    args = parser.parse_args()
    asyncio.run(_main(args.world, args.output, args.merged_world_output))


if __name__ == "__main__":
    main()
