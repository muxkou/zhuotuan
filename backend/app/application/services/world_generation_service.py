import json

from backend.app.application.services.prompt_loader import load_prompt
from backend.app.application.services.response_normalizers import normalize_world_payload
from backend.app.domain.enums.game import ArtifactSource
from backend.app.domain.schemas.generation import QuickStartInput, WorldGenerationOutput
from backend.app.domain.schemas.world import WorldSchema
from backend.app.infra.llm.llm_client import LLMClient


class WorldGenerationService:
    """根据快速开团输入生成世界草案。"""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    async def generate(self, quick_start: QuickStartInput) -> WorldGenerationOutput:
        system_prompt = load_prompt("world_generation.md")
        user_prompt = json.dumps(quick_start.model_dump(mode="json"), ensure_ascii=False, indent=2)
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
        )
        world = WorldSchema.model_validate(normalize_world_payload(raw_payload))
        world = world.model_copy(update={"source": ArtifactSource.LLM})
        return WorldGenerationOutput(world=world, raw_text=raw_text)
