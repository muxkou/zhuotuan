import json
from pathlib import Path
from typing import Any

from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.session import SessionSnapshotSchema
from backend.app.domain.schemas.world import WorldSchema


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_ruleset(data: dict) -> RuleSetSchema:
    return RuleSetSchema.model_validate(data)


def validate_world(data: dict) -> WorldSchema:
    return WorldSchema.model_validate(data)


def validate_module(data: dict) -> ModuleBlueprintSchema:
    return ModuleBlueprintSchema.model_validate(data)


def validate_character(data: dict) -> CharacterSheetSchema:
    return CharacterSheetSchema.model_validate(data)


def validate_session_snapshot(data: dict) -> SessionSnapshotSchema:
    return SessionSnapshotSchema.model_validate(data)


def validate_ruleset_file(path: str | Path) -> RuleSetSchema:
    return validate_ruleset(_load_json(path))


def validate_world_file(path: str | Path) -> WorldSchema:
    return validate_world(_load_json(path))


def validate_module_file(path: str | Path) -> ModuleBlueprintSchema:
    return validate_module(_load_json(path))


def validate_character_file(path: str | Path) -> CharacterSheetSchema:
    return validate_character(_load_json(path))


def validate_session_snapshot_file(path: str | Path) -> SessionSnapshotSchema:
    return validate_session_snapshot(_load_json(path))
