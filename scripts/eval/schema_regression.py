from pathlib import Path

from backend.app.application.validators.schema_validator import (
    validate_character_file,
    validate_module_file,
    validate_ruleset_file,
    validate_session_snapshot_file,
    validate_world_file,
)

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    validate_ruleset_file(ROOT / "artifacts/rulesets/min_ruleset.json")
    validate_world_file(ROOT / "artifacts/worlds/min_world.json")
    validate_module_file(ROOT / "artifacts/modules/min_module.json")
    validate_character_file(ROOT / "artifacts/characters/min_character.json")
    validate_session_snapshot_file(ROOT / "artifacts/sessions/min_session_snapshot.json")
    print("schema regression passed")


if __name__ == "__main__":
    main()
