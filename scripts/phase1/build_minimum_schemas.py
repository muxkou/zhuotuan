from pathlib import Path

from backend.app.domain.enums.game import ArtifactSource
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.module import ClueLink, ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import AttributeScore, RuleSetSchema, SkillBonus
from backend.app.domain.schemas.session import (
    CharacterRuntimeStateSchema,
    ClueStateSchema,
    NpcStateSchema,
    SessionSnapshotSchema,
    ThreatClockStateSchema,
)
from backend.app.domain.schemas.world import WorldSchema

ROOT = Path(__file__).resolve().parents[2]


def _write_json(relative_path: str, model) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    ruleset = RuleSetSchema(
        id="ruleset_light_cntrpg_v1",
        version="v1",
        source=ArtifactSource.SYSTEM,
        name="原创轻规则",
        description="阶段一短团使用的基础轻规则。",
        dice_formula="2d6",
        difficulty_bands={"easy": 7, "standard": 9, "hard": 11},
        attributes=["physique", "agility", "mind", "willpower", "social"],
        skills=[
            "investigation",
            "negotiation",
            "stealth",
            "combat",
            "medicine",
            "occult",
            "craft",
            "survival",
        ],
        resource_rules={"hp": 8, "mp": 8, "stress": 0, "fate_points": 1},
    )
    world = WorldSchema(
        id="world_tanxi_records_v1",
        version="v1",
        source=ArtifactSource.SYSTEM,
        name="檀溪异闻录",
        tagline="一个被水雾、旧宅、宗族和失踪传闻笼罩的江南古镇世界。",
        genre="中式怪谈调查",
        era="架空近现代",
        tone=["潮湿", "阴郁", "民俗悬疑"],
        public_rules=[
            "异常真实存在，但通常不会以直白方式出现。",
            "普通人会用风水、疯病、祖坟来解释异常。",
        ],
        hidden_rules=["异常往往与未竟仪式、旧案和家族禁忌有关。"],
        factions=["檀溪宗族", "镇公所", "白衣庙"],
        common_locations=["老宅", "祠堂", "码头", "档案室"],
        taboos=["不可在暴雨夜独自靠近后井。"],
        recommended_roles=["记者", "巡警", "医生", "民俗研究者"],
        narration_style={"horror_level": 2, "dialogue_style": "克制", "pacing": "steady"},
    )
    module = ModuleBlueprintSchema(
        id="module_rainy_house_v1",
        version="v1",
        source=ArtifactSource.SYSTEM,
        world_id=world.id,
        name="雨夜檀宅",
        player_count_min=2,
        player_count_max=4,
        duration_minutes=120,
        opening_hook="一名学生在暴雨夜失踪，留下一封提到檀宅后井的信。",
        core_secret="二十年前一场失败祭祀导致受害者怨念寄于后井，族老一直在掩盖真相。",
        major_conflict="玩家必须在暴雨与族老的阻挠下查明真相，阻止再一次献祭。",
        required_npcs=["npc_tan_mingyuan", "npc_lin_qinghe", "npc_old_doctor"],
        key_locations=["loc_main_hall", "loc_back_well", "loc_archive_room", "loc_white_temple"],
        key_clues=[
            ClueLink(
                clue_id="clue_letter",
                target_secret_id="secret_ritual",
                location_id="loc_main_hall",
            ),
            ClueLink(
                clue_id="clue_genealogy_gap",
                target_secret_id="secret_ritual",
                location_id="loc_main_hall",
                fallback_clue_ids=["clue_doctor_testimony"],
            ),
            ClueLink(
                clue_id="clue_ritual_text",
                target_secret_id="secret_ritual",
                location_id="loc_white_temple",
            ),
        ],
        threat_clock_id="clock_rain_ritual",
        endings={
            "good": "揭露真相并阻止再次献祭。",
            "partial": "救下关键角色，但真相未能完全公开。",
            "bad": "封井仪式完成，真相再次被掩盖。",
        },
        ai_do_not_change=["核心秘密不可改写", "族老不是无辜者", "关键线索不可删除"],
        ai_freedom_level="standard",
    )
    character = CharacterSheetSchema(
        id="char_chenyan_v1",
        version="v1",
        source=ArtifactSource.SYSTEM,
        name="陈砚",
        identity="外地记者",
        concept="为了调查妹妹旧案来到檀溪镇的年轻记者。",
        personality_tags=["冷静", "执拗", "不轻信权威"],
        module_motivation="失踪学生寄来的信提到了妹妹当年也出现过的地点，我必须查清楚。",
        attributes=AttributeScore(physique=0, agility=1, mind=2, willpower=1, social=0),
        skills=SkillBonus(investigation=2, negotiation=1, occult=1),
        strengths=["善于从细节中发现矛盾。"],
        weaknesses=["一旦涉及妹妹就会失去冷静。"],
        fears=["害怕发现妹妹早已死去。"],
        secret="我其实怀疑妹妹的案子和檀溪宗族有关。",
        relationships=[{"target": "npc_lin_qinghe", "type": "共情", "note": "都失去了重要亲人"}],
        inventory=["记者证", "旧相机", "钢笔", "失踪学生来信"],
    )
    snapshot = SessionSnapshotSchema(
        id="session_snapshot_rainy_house_001",
        version="v1",
        source=ArtifactSource.SYSTEM,
        table_id="table_rainy_house_001",
        session_id="session_001",
        clue_states=[
            ClueStateSchema(
                clue_id="clue_letter",
                status="discovered",
                discovered_by=[character.id],
                public_notes=["信中提到了檀宅后井传来母亲的声音。"],
            )
        ],
        npc_states=[
            NpcStateSchema(
                npc_id="npc_tan_mingyuan",
                attitude="neutral",
                current_status="watchful",
                public_summary="表面上配合调查，但显然不想让外人深挖。",
            )
        ],
        character_states=[
            CharacterRuntimeStateSchema(
                character_id=character.id,
                hp=8,
                mp=8,
                stress=0,
            )
        ],
        threat_clock_state=ThreatClockStateSchema(
            threat_clock_id="clock_rain_ritual",
            current_stage=0,
            stage_label="暴雨将至",
            triggered_events=[],
        ),
        unresolved_questions=["二十年前被抹去的女子是谁？"],
    )

    _write_json("artifacts/rulesets/min_ruleset.json", ruleset)
    _write_json("artifacts/worlds/min_world.json", world)
    _write_json("artifacts/modules/min_module.json", module)
    _write_json("artifacts/characters/min_character.json", character)
    _write_json("artifacts/sessions/min_session_snapshot.json", snapshot)


if __name__ == "__main__":
    main()
