import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_min_world_shape_is_stable() -> None:
    data = json.loads((ROOT / "artifacts/worlds/min_world.json").read_text(encoding="utf-8"))
    assert sorted(data.keys()) == [
        "character_creation_profile",
        "common_locations",
        "created_at",
        "era",
        "factions",
        "genre",
        "hidden_rules",
        "id",
        "name",
        "narration_style",
        "public_rules",
        "recommended_roles",
        "source",
        "special_status_catalog",
        "taboos",
        "tagline",
        "tone",
        "version",
    ]


def test_min_module_shape_is_stable() -> None:
    data = json.loads((ROOT / "artifacts/modules/min_module.json").read_text(encoding="utf-8"))
    assert sorted(data.keys()) == [
        "ai_do_not_change",
        "ai_freedom_level",
        "core_secret",
        "created_at",
        "duration_minutes",
        "endings",
        "id",
        "key_clues",
        "key_locations",
        "major_conflict",
        "name",
        "opening_hook",
        "player_count_max",
        "player_count_min",
        "required_npcs",
        "source",
        "threat_clock_id",
        "version",
        "world_id",
    ]
