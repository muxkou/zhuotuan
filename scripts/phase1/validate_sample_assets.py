import argparse
from pathlib import Path
from time import perf_counter

from backend.app.application.validators.schema_validator import (
    validate_character_file,
    validate_module_file,
    validate_ruleset_file,
    validate_session_snapshot_file,
    validate_world_file,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.common import ValidationReport



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started_at = perf_counter()

    validate_ruleset_file(args.input / "rulesets" / "min_ruleset.json")
    validate_world_file(args.input / "worlds" / "min_world.json")
    validate_module_file(args.input / "modules" / "min_module.json")
    validate_character_file(args.input / "characters" / "min_character.json")
    validate_session_snapshot_file(args.input / "sessions" / "min_session_snapshot.json")

    elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
    report = ValidationReport(
        status=ValidationStatus.PASS,
        suggestions=["all minimum phase 1 assets are schema-valid"],
        metrics={"elapsed_ms": elapsed_ms, "validated_assets": 5},
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
