import argparse
import asyncio
import json
from pathlib import Path

from backend.app.application.services.world_generation_service import WorldGenerationService
from backend.app.domain.schemas.generation import QuickStartInput


async def _main(input_path: Path, output_path: Path) -> None:
    quick_start = QuickStartInput.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
    service = WorldGenerationService()
    result = await service.generate(quick_start)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.world.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(_main(args.input, args.output))


if __name__ == "__main__":
    main()
