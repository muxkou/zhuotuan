import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

from backend.app.application.services.module_generation_pipeline import ModuleGenerationPipeline
from backend.app.application.services.world_generation_service import WorldGenerationService
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.generation import QuickStartInput


async def _main(cases_dir: Path, output_path: Path, max_cases: int | None) -> None:
    world_service = WorldGenerationService()
    module_pipeline = ModuleGenerationPipeline()

    case_paths = sorted(cases_dir.glob("quickstart_*.json"))
    if max_cases is not None:
        case_paths = case_paths[:max_cases]

    results: list[dict] = []
    for path in case_paths:
        quick_start = QuickStartInput.model_validate(json.loads(path.read_text(encoding="utf-8")))
        started_at = perf_counter()
        try:
            world_result = await world_service.generate(quick_start)
            module_result = await module_pipeline.run(
                quick_start,
                world_result.world,
                allow_repair=True,
            )
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
            results.append(
                {
                    "case_id": quick_start.case_id,
                    "status": module_result.final_report.status,
                    "clue_path_count": module_result.final_report.clue_path_count,
                    "elapsed_ms": elapsed_ms,
                    "repair_attempted": module_result.repair_attempted,
                    "repaired": module_result.repaired,
                    "initial_status": module_result.initial_report.status,
                    "final_status": module_result.final_report.status,
                }
            )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
            results.append(
                {
                    "case_id": quick_start.case_id,
                    "status": ValidationStatus.FAIL,
                    "clue_path_count": 0,
                    "elapsed_ms": elapsed_ms,
                    "repair_attempted": False,
                    "repaired": False,
                    "error": str(exc),
                }
            )

    total = len(results)
    pass_count = sum(1 for item in results if item["status"] == ValidationStatus.PASS)
    warn_count = sum(1 for item in results if item["status"] == ValidationStatus.WARN)
    fail_count = sum(1 for item in results if item["status"] == ValidationStatus.FAIL)
    summary = {
        "total_cases": total,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-dir", type=Path, default=Path("artifacts/cases"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-cases", type=int, default=None)
    args = parser.parse_args()
    asyncio.run(_main(args.cases_dir, args.output, args.max_cases))


if __name__ == "__main__":
    main()
