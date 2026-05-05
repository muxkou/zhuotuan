import json
from typing import Any

from backend.app.application.services.prompt_loader import load_prompt
from backend.app.application.services.response_normalizers import (
    normalize_character_creation_profile_payload,
)
from backend.app.domain.schemas.generation import CharacterCreationProfileGenerationOutput
from backend.app.domain.schemas.world import CharacterCreationProfile, WorldSchema
from backend.app.infra.llm.llm_client import LLMClient


class CharacterCreationProfileGenerationService:
    """根据已生成世界补充车卡属性、技能和点数规则。"""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def _prepare_payload(self, raw_payload: dict[str, Any], world: WorldSchema) -> dict:
        payload = raw_payload.get("character_creation_profile", raw_payload)
        normalized = normalize_character_creation_profile_payload(
            payload,
            {"recommended_roles": world.recommended_roles},
        )
        if not normalized.get("base_attributes"):
            normalized["base_attributes"] = world.character_creation_profile.base_attributes
        return normalized

    async def generate(self, world: WorldSchema) -> CharacterCreationProfileGenerationOutput:
        system_prompt = load_prompt("character_creation_profile_generation.md")
        user_prompt = json.dumps(world.model_dump(mode="json"), ensure_ascii=False, indent=2)
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )
        profile = CharacterCreationProfile.model_validate(
            self._prepare_payload(raw_payload, world)
        )
        return CharacterCreationProfileGenerationOutput(profile=profile, raw_text=raw_text)
