import argparse
import asyncio
import json
from pathlib import Path

from backend.app.application.services.module_generation_service import ModuleGenerationService
from backend.app.domain.schemas.generation import QuickStartInput
from backend.app.domain.schemas.world import WorldSchema

"""
单 case 基于 world 生成 module
"""

async def _main(input_path: Path, world_path: Path, output_path: Path) -> None:
    quick_start = QuickStartInput.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    service = ModuleGenerationService()
    result = await service.generate(quick_start, world)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.module.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(_main(args.input, args.world, args.output))


if __name__ == "__main__":
    main()
