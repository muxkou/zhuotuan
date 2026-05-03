import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from backend.app.application.services.module_generation_pipeline import (
    ModuleGenerationPipeline,
)
from backend.app.application.services.world_generation_service import (
    WorldGenerationService,
)
from backend.app.domain.schemas.generation import QuickStartInput


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _log(message: str) -> None:
    timestamp = datetime.now(UTC).strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


async def _main(input_path: Path, output_dir: Path, allow_repair: bool) -> None:
    _log(f"读取快速开团输入: {input_path}")
    quick_start = QuickStartInput.model_validate(
        json.loads(input_path.read_text(encoding="utf-8"))
    )
    run_dir = output_dir / quick_start.case_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _log(f"本次 case_id: {quick_start.case_id}")
    _log(f"产物输出目录: {run_dir}")
    _log(f"repair pass: {'开启' if allow_repair else '关闭'}")

    world_service = WorldGenerationService()
    module_pipeline = ModuleGenerationPipeline()

    flow_started_at = perf_counter()

    _write_json(
        run_dir / "quick_start_input.json",
        quick_start.model_dump(mode="json"),
    )

    _log("开始生成 world")
    world_started_at = perf_counter()
    world_result = await world_service.generate(quick_start)
    world_elapsed_ms = round((perf_counter() - world_started_at) * 1000, 3)
    (run_dir / "world.json").write_text(
        world_result.world.model_dump_json(indent=2),
        encoding="utf-8",
    )
    if world_result.raw_text is not None:
        (run_dir / "world_raw_response.txt").write_text(
            world_result.raw_text,
            encoding="utf-8",
        )
    _log(
        f"world 生成完成: status=pass, elapsed_ms={world_elapsed_ms}, file={run_dir / 'world.json'}"
    )

    _log("开始执行 module 生成主链路")
    module_started_at = perf_counter()
    module_result = await module_pipeline.run(
        quick_start,
        world_result.world,
        allow_repair=allow_repair,
        progress_hook=_log,
    )
    module_elapsed_ms = round((perf_counter() - module_started_at) * 1000, 3)
    (run_dir / "module.json").write_text(
        module_result.module.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (run_dir / "module_generation_report.json").write_text(
        module_result.model_dump_json(indent=2),
        encoding="utf-8",
    )
    if module_result.initial_raw_text is not None:
        (run_dir / "module_initial_raw_response.txt").write_text(
            module_result.initial_raw_text,
            encoding="utf-8",
        )
    if module_result.repair_raw_text is not None:
        (run_dir / "module_repair_raw_response.txt").write_text(
            module_result.repair_raw_text,
            encoding="utf-8",
        )
    _log(
        "module 链路完成: "
        f"initial={module_result.initial_report.status}, "
        f"final={module_result.final_report.status}, "
        f"repair_attempted={module_result.repair_attempted}, "
        f"repaired={module_result.repaired}, "
        f"elapsed_ms={module_elapsed_ms}"
    )

    total_elapsed_ms = round((perf_counter() - flow_started_at) * 1000, 3)
    summary = {
        "case_id": quick_start.case_id,
        "created_at": _timestamp(),
        "input_file": str(input_path),
        "run_dir": str(run_dir),
        "allow_repair": allow_repair,
        "world": {
            "status": "pass",
            "elapsed_ms": world_elapsed_ms,
            "artifact": str(run_dir / "world.json"),
        },
        "module": {
            "initial_status": module_result.initial_report.status,
            "final_status": module_result.final_report.status,
            "repair_attempted": module_result.repair_attempted,
            "repaired": module_result.repaired,
            "elapsed_ms": module_elapsed_ms,
            "artifact": str(run_dir / "module.json"),
            "report_artifact": str(run_dir / "module_generation_report.json"),
        },
        "pipeline_placeholders": {
            "character_pipeline": "pending",
            "session_zero": "pending",
            "turn_loop": "pending",
            "session_report": "pending",
        },
        "total_elapsed_ms": total_elapsed_ms,
    }
    _write_json(run_dir / "flow_summary.json", summary)

    _log(f"全流程完成，总耗时: {total_elapsed_ms} ms")
    _log(f"流程摘要文件: {run_dir / 'flow_summary.json'}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the current phase-1 end-to-end quickstart flow."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/runs"),
    )
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Disable the automatic repair pass for warn/fail modules.",
    )
    args = parser.parse_args()

    asyncio.run(
        _main(
            input_path=args.input,
            output_dir=args.output_dir,
            allow_repair=not args.no_repair,
        )
    )


if __name__ == "__main__":
    main()
