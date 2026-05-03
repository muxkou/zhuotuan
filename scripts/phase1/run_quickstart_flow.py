import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.application.services.module_generation_pipeline import (
    ModuleGenerationPipeline,
)
from backend.app.application.services.world_generation_service import (
    WorldGenerationService,
)
from backend.app.domain.schemas.generation import CharacterQuestionnaire, QuickStartInput
from backend.app.domain.schemas.ruleset import RuleSetSchema


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _log(message: str) -> None:
    timestamp = datetime.now(UTC).strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


async def _main(
    input_path: Path,
    output_dir: Path,
    allow_repair: bool,
    questionnaire_path: Path | None,
    ruleset_path: Path,
) -> None:
    _log(f"读取快速开团输入: {input_path}")
    quick_start = QuickStartInput.model_validate(
        json.loads(input_path.read_text(encoding="utf-8"))
    )
    run_dir = output_dir / quick_start.case_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _log(f"本次 case_id: {quick_start.case_id}")
    _log(f"产物输出目录: {run_dir}")
    _log(f"repair pass: {'开启' if allow_repair else '关闭'}")
    _log(
        "角色链路: "
        + (f"开启，questionnaire={questionnaire_path}" if questionnaire_path else "未开启")
    )

    world_service = WorldGenerationService()
    module_pipeline = ModuleGenerationPipeline()
    character_pipeline = CharacterReviewPipeline()

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

    character_summary: dict[str, object] | str = "pending"
    if questionnaire_path is not None:
        _log("开始执行 character 生成与审核链路")
        questionnaire = CharacterQuestionnaire.model_validate(
            json.loads(questionnaire_path.read_text(encoding="utf-8"))
        )
        ruleset = RuleSetSchema.model_validate(
            json.loads(ruleset_path.read_text(encoding="utf-8"))
        )
        (run_dir / "character_questionnaire.json").write_text(
            questionnaire.model_dump_json(indent=2),
            encoding="utf-8",
        )

        character_started_at = perf_counter()
        character_result = await character_pipeline.run(
            questionnaire,
            world_result.world,
            module_result.module,
            ruleset,
            allow_repair=allow_repair,
            progress_hook=_log,
        )
        character_elapsed_ms = round((perf_counter() - character_started_at) * 1000, 3)
        (run_dir / "character.json").write_text(
            character_result.character.model_dump_json(indent=2),
            encoding="utf-8",
        )
        (run_dir / "character_generation_report.json").write_text(
            character_result.model_dump_json(indent=2),
            encoding="utf-8",
        )
        if character_result.initial_raw_text is not None:
            (run_dir / "character_initial_raw_response.txt").write_text(
                character_result.initial_raw_text,
                encoding="utf-8",
            )
        if character_result.repair_raw_text is not None:
            (run_dir / "character_repair_raw_response.txt").write_text(
                character_result.repair_raw_text,
                encoding="utf-8",
            )
        _log(
            "character 链路完成: "
            f"initial={character_result.initial_review_report.review_result}, "
            f"final={character_result.final_review_report.review_result}, "
            f"repair_attempted={character_result.repair_attempted}, "
            f"repaired={character_result.repaired}, "
            f"elapsed_ms={character_elapsed_ms}"
        )
        character_summary = {
            "initial_status": character_result.initial_review_report.status,
            "final_status": character_result.final_review_report.status,
            "initial_review_result": character_result.initial_review_report.review_result,
            "final_review_result": character_result.final_review_report.review_result,
            "repair_attempted": character_result.repair_attempted,
            "repaired": character_result.repaired,
            "elapsed_ms": character_elapsed_ms,
            "artifact": str(run_dir / "character.json"),
            "report_artifact": str(run_dir / "character_generation_report.json"),
        }

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
        "character": character_summary,
        "pipeline_placeholders": {
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
        "--questionnaire",
        type=Path,
        default=None,
        help="Optional questionnaire file to run the phase-1 character pipeline.",
    )
    parser.add_argument(
        "--ruleset",
        type=Path,
        default=Path("artifacts/rulesets/min_ruleset.json"),
        help="Ruleset used by the character pipeline.",
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
            questionnaire_path=args.questionnaire,
            ruleset_path=args.ruleset,
        )
    )


if __name__ == "__main__":
    main()
