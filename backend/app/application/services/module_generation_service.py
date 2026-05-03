import json

from backend.app.application.services.prompt_loader import load_prompt
from backend.app.application.services.response_normalizers import normalize_module_payload
from backend.app.domain.enums.game import ArtifactSource, ValidationStatus
from backend.app.domain.schemas.generation import ModuleGenerationOutput, QuickStartInput
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.world import WorldSchema
from backend.app.infra.llm.llm_client import LLMClient


class ModuleGenerationService:
    """根据快速开团输入和世界草案生成模组蓝图。"""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    async def generate(
        self,
        quick_start: QuickStartInput,
        world: WorldSchema,
    ) -> ModuleGenerationOutput:
        system_prompt = load_prompt("module_generation.md")
        user_prompt = json.dumps(
            {
                "quick_start": quick_start.model_dump(mode="json"),
                "world": world.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        )
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
        )
        module = ModuleBlueprintSchema.model_validate(normalize_module_payload(raw_payload))
        module = module.model_copy(
            update={
                "world_id": world.id,
                "source": ArtifactSource.LLM,
            }
        )
        return ModuleGenerationOutput(module=module, raw_text=raw_text)

    async def repair(
        self,
        quick_start: QuickStartInput,
        world: WorldSchema,
        broken_module: ModuleBlueprintSchema,
        validation_summary: dict,
    ) -> ModuleGenerationOutput:
        system_prompt = load_prompt("module_repair.md")
        user_prompt = json.dumps(
            {
                "quick_start": quick_start.model_dump(mode="json"),
                "world": world.model_dump(mode="json"),
                "module": broken_module.model_dump(mode="json"),
                "validation_summary": validation_summary,
                "target_status": ValidationStatus.PASS.value,
            },
            ensure_ascii=False,
            indent=2,
        )
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,
        )
        module = ModuleBlueprintSchema.model_validate(normalize_module_payload(raw_payload))
        module = module.model_copy(
            update={
                "world_id": world.id,
                "source": ArtifactSource.LLM,
            }
        )
        return ModuleGenerationOutput(module=module, raw_text=raw_text)
