from backend.app.application.validators.module_playability_validator import (
    ModulePlayabilityValidator,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.module import ClueLink, ModuleBlueprintSchema
from backend.app.domain.schemas.world import WorldSchema


def make_world() -> WorldSchema:
    return WorldSchema(
        id="world_1",
        name="檀溪异闻录",
        tagline="测试世界",
        genre="中式怪谈",
        era="架空近现代",
        tone=["阴郁"],
        public_rules=["异常真实存在。"],
        factions=["宗族"],
        common_locations=["旧宅"],
        taboos=["不可夜探后井。"],
        recommended_roles=["记者"],
        narration_style={"horror_level": 2, "dialogue_style": "克制", "pacing": "steady"},
    )


def make_module(clue_count: int = 3, with_fallback: bool = True) -> ModuleBlueprintSchema:
    clue_links = []
    for index in range(clue_count):
        clue_links.append(
            ClueLink(
                clue_id=f"clue_{index}",
                target_secret_id="secret_1",
                location_id=f"loc_{index}",
                fallback_clue_ids=["backup_1"] if with_fallback and index == 0 else [],
            )
        )
    return ModuleBlueprintSchema(
        id="module_1",
        world_id="world_1",
        name="雨夜檀宅",
        player_count_min=2,
        player_count_max=4,
        duration_minutes=120,
        opening_hook="有人失踪。",
        core_secret="旧案与祭祀有关。",
        major_conflict="必须阻止再一次献祭。",
        required_npcs=["npc_1"],
        key_locations=["loc_1"],
        key_clues=clue_links,
        threat_clock_id="clock_1",
        endings={"good": "好", "partial": "中", "bad": "差"},
        ai_do_not_change=["核心秘密不可改写"],
        ai_freedom_level="standard",
    )


def test_module_playability_validator_passes_good_module() -> None:
    report = ModulePlayabilityValidator().validate(make_module(), make_world())
    assert report.status == ValidationStatus.PASS
    assert report.clue_path_count == 3


def test_module_playability_validator_warns_on_low_clues() -> None:
    report = ModulePlayabilityValidator().validate(make_module(clue_count=2), make_world())
    assert report.status == ValidationStatus.WARN
    assert report.clue_path_count == 2


def test_module_playability_validator_warns_on_missing_fallback() -> None:
    report = ModulePlayabilityValidator().validate(make_module(with_fallback=False), make_world())
    assert report.status == ValidationStatus.WARN
