from backend.app.application.services.module_generation_pipeline import ModuleGenerationPipeline
from backend.app.application.services.module_generation_service import ModuleGenerationService
from backend.app.application.services.world_generation_service import WorldGenerationService
from backend.app.domain.schemas.generation import QuickStartInput
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.world import WorldSchema


class FakeLLMClient:
    def __init__(self, outputs: list[object]):
        self.outputs = outputs

    async def generate_json_dict(self, **kwargs):
        output = self.outputs.pop(0)
        if isinstance(output, dict):
            return output, '{"mocked": true}'
        return output.model_dump(mode="json"), '{"mocked": true}'


def make_quick_start() -> QuickStartInput:
    return QuickStartInput(
        case_id="case_001",
        genre="中式怪谈",
        duration_minutes=90,
        player_count=3,
        tone=["潮湿", "悬疑"],
        inspiration="江南古镇、旧宅、暴雨、失踪案",
        horror_level="medium",
    )


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


def make_module() -> ModuleBlueprintSchema:
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


async def test_world_generation_service_returns_valid_output() -> None:
    service = WorldGenerationService(llm_client=FakeLLMClient([make_world()]))
    result = await service.generate(make_quick_start())
    assert result.world.id.startswith("world_")
    assert result.world.id != "world_1"
    assert result.world.source == "llm"


async def test_module_generation_service_returns_valid_output() -> None:
    world = make_world()
    service = ModuleGenerationService(llm_client=FakeLLMClient([make_module()]))
    result = await service.generate(make_quick_start(), world)
    assert result.module.id.startswith("module_")
    assert result.module.world_id == world.id
    assert result.module.threat_clock_id.startswith("clock_")
    assert all(clue.clue_id.startswith("clue_") for clue in result.module.key_clues)
    assert result.module.source == "llm"


async def test_module_generation_service_normalizes_float_ai_freedom_level() -> None:
    world = make_world()
    module = make_module().model_dump(mode="json")
    module["ai_freedom_level"] = 0.2
    service = ModuleGenerationService(llm_client=FakeLLMClient([module]))
    result = await service.generate(make_quick_start(), world)
    assert result.module.ai_freedom_level == "conservative"


async def test_module_generation_pipeline_repairs_warn_module() -> None:
    world = make_world()
    broken_module = make_module()
    broken_module.key_clues[0].fallback_clue_ids = []
    broken_module.key_clues[1].fallback_clue_ids = []
    broken_module.key_clues[2].fallback_clue_ids = []
    repaired_module = make_module()

    pipeline = ModuleGenerationPipeline(
        module_service=ModuleGenerationService(
            llm_client=FakeLLMClient([broken_module, repaired_module])
        )
    )

    result = await pipeline.run(make_quick_start(), world, allow_repair=True)

    assert result.repair_attempted is True
    assert result.repaired is True
    assert result.initial_report.status == "warn"
    assert result.final_report.status == "pass"
