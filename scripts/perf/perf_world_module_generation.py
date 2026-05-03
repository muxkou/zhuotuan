import argparse
import asyncio
import json
from pathlib import Path
from statistics import mean
from time import perf_counter

from backend.app.application.services.module_generation_service import ModuleGenerationService
from backend.app.application.services.world_generation_service import WorldGenerationService
from backend.app.domain.schemas.generation import QuickStartInput


async def _main(input_path: Path, runs: int, output_path: Path) -> None:
    quick_start = QuickStartInput.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
    world_service = WorldGenerationService()
    module_service = ModuleGenerationService()
    latencies: list[float] = []

    for _ in range(runs):
        started_at = perf_counter()
        world_result = await world_service.generate(quick_start)
        await module_service.generate(quick_start, world_result.world)
        latencies.append(round((perf_counter() - started_at) * 1000, 3))

    summary = {
        "case_id": quick_start.case_id,
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
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(_main(args.input, args.runs, args.output))


if __name__ == "__main__":
    main()
