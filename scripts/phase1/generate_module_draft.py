import argparse
import asyncio
import json
from pathlib import Path

from backend.app.application.services.module_generation_pipeline import ModuleGenerationPipeline
from backend.app.domain.schemas.generation import QuickStartInput
from backend.app.domain.schemas.world import WorldSchema


async def _main(input_path: Path, world_path: Path, output_path: Path) -> None:
    quick_start = QuickStartInput.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
    world = WorldSchema.model_validate(json.loads(world_path.read_text(encoding="utf-8")))
    pipeline = ModuleGenerationPipeline()
    result = await pipeline.run(quick_start, world, allow_repair=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.module.model_dump_json(indent=2), encoding="utf-8")

    report_path = output_path.with_name(f"{output_path.stem}_generation_report.json")
    report_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(_main(args.input, args.world, args.output))


if __name__ == "__main__":
    main()
