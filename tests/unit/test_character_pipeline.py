from backend.app.application.services.character_generation_service import (
    CharacterGenerationService,
)
from backend.app.application.services.character_review_pipeline import (
    CharacterReviewPipeline,
)
from backend.app.application.services.manual_character_card_service import (
    ManualCharacterCardService,
)
from backend.app.application.validators.character_module_validator import (
    CharacterModuleValidator,
)
from backend.app.application.validators.character_rules_validator import (
    CharacterRulesValidator,
)
from backend.app.application.validators.character_world_profile_validator import (
    CharacterWorldProfileValidator,
)
from backend.app.application.validators.character_world_validator import (
    CharacterWorldValidator,
)
from backend.app.domain.schemas.character import CharacterSheetSchema, ManualCharacterCardInput
from backend.app.domain.schemas.generation import CharacterQuestionnaire
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


class FakeLLMClient:
    def __init__(self, outputs: list[object]):
        self.outputs = outputs

    async def generate_json_dict(self, **kwargs):
        output = self.outputs.pop(0)
        return output.model_dump(mode="json"), '{"mocked": true}'


def make_questionnaire() -> CharacterQuestionnaire:
    return CharacterQuestionnaire(
        case_id="case_001",
        player_id="player_001",
        name_hint="陈砚",
        identity_answer="外地记者",
        motivation_answer="我必须查清楚和妹妹旧案有关的失踪事件。",
        specialty_answer="调查与追问真相",
        fear_answer="害怕亲人早已被牺牲",
        relationship_answer="和本地医生有旧识",
        secret_answer="我怀疑宗族篡改过记录",
    )


def make_ruleset() -> RuleSetSchema:
    return RuleSetSchema(
        id="ruleset_1",
        name="原创轻规则",
        description="测试规则",
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


def make_world() -> WorldSchema:
    return WorldSchema(
        id="world_1",
        name="檀溪异闻录",
        tagline="测试世界",
        genre="中式怪谈",
        era="架空近现代",
        tone=["阴郁"],
        public_rules=["异常真实存在，但普通人没有稳定超能力。"],
        factions=["宗族"],
        common_locations=["旧宅"],
        taboos=["不可夜探后井。"],
        recommended_roles=["外地记者", "医生", "巡警"],
        narration_style={"horror_level": 2, "dialogue_style": "克制", "pacing": "steady"},
        character_creation_profile={
            "base_attributes": [
                {
                    "key": "physique",
                    "label": "体魄",
                    "description": "力量与耐力。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "偏弱"},
                        {"min_value": 1, "max_value": 2, "summary": "正常"},
                        {"min_value": 3, "max_value": 3, "summary": "强健"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "agility",
                    "label": "机敏",
                    "description": "反应与潜行。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "偏慢"},
                        {"min_value": 1, "max_value": 2, "summary": "正常"},
                        {"min_value": 3, "max_value": 3, "summary": "灵活"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "mind",
                    "label": "心智",
                    "description": "理解与推理。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "偏慢"},
                        {"min_value": 1, "max_value": 2, "summary": "正常"},
                        {"min_value": 3, "max_value": 3, "summary": "敏锐"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "willpower",
                    "label": "意志",
                    "description": "抗压和定力。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "偏弱"},
                        {"min_value": 1, "max_value": 2, "summary": "正常"},
                        {"min_value": 3, "max_value": 3, "summary": "坚定"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "social",
                    "label": "社交",
                    "description": "表达与共情。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "木讷"},
                        {"min_value": 1, "max_value": 2, "summary": "正常"},
                        {"min_value": 3, "max_value": 3, "summary": "老练"},
                    ],
                    "is_core": True,
                },
            ],
            "world_specific_attributes": [
                {
                    "key": "spirit_sensitivity",
                    "label": "灵感",
                    "description": "对异常与神话痕迹的敏感度。",
                    "min_value": 0,
                    "max_value": 2,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "迟钝"},
                        {"min_value": 1, "max_value": 2, "summary": "敏感"},
                    ],
                    "is_core": False,
                }
            ],
            "total_attribute_budget_min": 0,
            "total_attribute_budget_max": 5,
            "identity_guidelines": ["优先选择能自然介入调查的身份。"],
            "forbidden_character_elements": ["明确可控的强超自然能力"],
            "total_skill_points": 6,
        },
    )


def make_module() -> ModuleBlueprintSchema:
    return ModuleBlueprintSchema(
        id="module_1",
        world_id="world_1",
        name="雨夜檀宅",
        player_count_min=2,
        player_count_max=4,
        duration_minutes=120,
        opening_hook="一名学生失踪后，家属向你们发出求助。",
        core_secret="旧案与宗族献祭有关。",
        major_conflict="必须阻止再一次献祭。",
        required_npcs=["npc_1"],
        key_locations=["loc_1"],
        key_clues=[
            {
                "clue_id": "clue_1",
                "target_secret_id": "secret_1",
                "location_id": "loc_1",
                "fallback_clue_ids": ["clue_b"],
            },
            {
                "clue_id": "clue_2",
                "target_secret_id": "secret_1",
                "location_id": "loc_2",
                "fallback_clue_ids": [],
            },
            {
                "clue_id": "clue_3",
                "target_secret_id": "secret_1",
                "location_id": "loc_3",
                "fallback_clue_ids": [],
            },
        ],
        threat_clock_id="clock_1",
        endings={"good": "好", "partial": "中", "bad": "差"},
        ai_do_not_change=["核心秘密不可改写"],
        ai_freedom_level="standard",
    )


def make_character(**overrides) -> CharacterSheetSchema:
    payload = {
        "id": "char_1",
        "name": "陈砚",
        "identity": "外地记者",
        "concept": "为了调查妹妹旧案回到檀溪镇的年轻记者。",
        "personality_tags": ["冷静", "执拗"],
        "module_motivation": "失踪案线索和妹妹旧案重叠，我必须参与调查并盯住宗族的反应。",
        "attributes": {
            "physique": 0,
            "agility": 1,
            "mind": 2,
            "willpower": 1,
            "social": 0,
        },
        "extra_attributes": {},
        "skills": {
            "investigation": 2,
            "negotiation": 1,
            "stealth": 0,
            "combat": 0,
            "medicine": 0,
            "occult": 1,
            "craft": 0,
            "survival": 0,
        },
        "strengths": ["善于从旧报道里找矛盾。"],
        "weaknesses": ["一旦涉及妹妹就容易失去冷静。"],
        "fears": ["害怕失踪案背后又是一场被默许的牺牲。"],
        "secret": "我怀疑有人篡改过旧档案。",
        "relationships": [
            {
                "target": "npc_doctor",
                "type": "旧识",
                "note": "曾在一次采访中帮过我。",
            }
        ],
        "inventory": ["记者证", "旧相机"],
    }
    payload.update(overrides)
    return CharacterSheetSchema.model_validate(payload)


def test_character_rules_validator_flags_overpowered_sheet() -> None:
    character = make_character(
        attributes={"physique": 3, "agility": 3, "mind": 3, "willpower": 3, "social": 3},
        skills={
            "investigation": 2,
            "negotiation": 2,
            "stealth": 2,
            "combat": 2,
            "medicine": 2,
            "occult": 2,
            "craft": 2,
            "survival": 2,
        },
    )
    report = CharacterRulesValidator().validate(character, make_ruleset())
    assert report.status == "fail"


def test_character_world_validator_flags_forbidden_superpower() -> None:
    character = make_character(
        concept="能够读心并提前看到命案的神秘调查员。",
        strengths=["预知未来的梦境。"],
    )
    report = CharacterWorldValidator().validate(character, make_world())
    assert report.status == "fail"


def test_character_world_profile_validator_accepts_world_specific_attribute() -> None:
    character = make_character(extra_attributes={"spirit_sensitivity": 1})
    report = CharacterWorldProfileValidator().validate(character, make_world())
    assert report.status == "pass"


def test_character_world_profile_validator_rejects_unknown_attribute() -> None:
    character = make_character(extra_attributes={"divinity": 2})
    report = CharacterWorldProfileValidator().validate(character, make_world())
    assert report.status == "fail"


def test_character_world_profile_validator_rejects_unknown_skill() -> None:
    character = make_character(skills={"dream_reading": 1})
    report = CharacterWorldProfileValidator().validate(character, make_world())
    assert report.status == "fail"


def test_character_world_profile_validator_rejects_skill_budget_overflow() -> None:
    character = make_character(
        skills={
            "investigation": 2,
            "negotiation": 2,
            "stealth": 2,
            "combat": 2,
        }
    )
    report = CharacterWorldProfileValidator().validate(character, make_world())
    assert report.status == "fail"


def test_manual_character_card_service_builds_reviewable_character() -> None:
    manual_input = ManualCharacterCardInput(
        case_id="case_001",
        player_id="player_001",
        name="陈砚",
        identity="外地记者",
        concept="为了调查妹妹旧案回到檀溪镇的年轻记者。",
        personality_tags=["冷静", "执拗"],
        module_motivation="失踪案线索和妹妹旧案重叠，我必须参与调查。",
        attributes={
            "physique": 0,
            "agility": 1,
            "mind": 2,
            "willpower": 1,
            "social": 0,
            "spirit_sensitivity": 1,
        },
        skills={"investigation": 2, "occult": 1},
        strengths=["善于从旧报道里找矛盾。"],
        weaknesses=["一旦涉及妹妹就容易失去冷静。"],
        fears=["害怕失踪案背后又是一场被默许的牺牲。"],
        secret="我怀疑有人篡改过旧档案。",
        relationships=[
            {"target": "npc_doctor", "type": "旧识", "note": "曾帮过我。"}
        ],
        inventory=["记者证", "旧相机"],
    )
    character = ManualCharacterCardService().build_character(manual_input, make_world())
    report = CharacterReviewPipeline().review(
        character,
        make_world(),
        make_module(),
        make_ruleset(),
    )
    assert character.id.startswith("char_")
    assert character.extra_attributes == {"spirit_sensitivity": 1}
    assert report.status in {"pass", "warn"}


def test_character_module_validator_flags_spoiler_character() -> None:
    character = make_character(
        secret="我早就知道旧案与宗族献祭有关，而且掌握完整名单。",
    )
    report = CharacterModuleValidator().validate(character, make_module())
    assert report.status == "fail"


def test_character_module_validator_flags_no_motivation() -> None:
    character = make_character(module_motivation="路过随便看看。")
    report = CharacterModuleValidator().validate(character, make_module())
    assert report.status == "fail"


async def test_character_generation_service_returns_valid_output() -> None:
    service = CharacterGenerationService(llm_client=FakeLLMClient([make_character()]))
    result = await service.generate(
        make_questionnaire(),
        make_world(),
        make_module(),
        make_ruleset(),
    )
    assert result.character.identity == "外地记者"
    assert result.character.source == "llm"


async def test_character_review_pipeline_repairs_bad_character() -> None:
    bad_character = make_character(
        module_motivation="路过随便看看。",
        secret="我早就知道旧案与宗族献祭有关，而且掌握完整名单。",
    )
    repaired_character = make_character()
    pipeline = CharacterReviewPipeline(
        generation_service=CharacterGenerationService(
            llm_client=FakeLLMClient([bad_character, repaired_character])
        )
    )

    run_output = await pipeline.run(
        make_questionnaire(),
        make_world(),
        make_module(),
        make_ruleset(),
        allow_repair=True,
    )

    assert run_output.repair_attempted is True
    assert run_output.repaired is True
    assert run_output.initial_review_report.review_result == "needs_revision"
    assert run_output.final_review_report.review_result in {"approved", "enhance"}


def test_character_review_pipeline_detects_roster_conflict() -> None:
    pipeline = CharacterReviewPipeline()
    existing_character = make_character()
    conflicting_character = make_character(id="char_2", name="陈砚")
    report = pipeline.review(
        conflicting_character,
        make_world(),
        make_module(),
        make_ruleset(),
        existing_characters=[existing_character],
        queue_position=2,
    )
    assert report.status == "fail"
    assert report.queue_position == 2
    assert report.roster_conflicts
