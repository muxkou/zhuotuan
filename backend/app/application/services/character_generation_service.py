import json

from backend.app.application.services.prompt_loader import load_prompt
from backend.app.application.services.response_normalizers import normalize_character_payload
from backend.app.domain.enums.game import ArtifactSource
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.generation import (
    CharacterGenerationOutput,
    CharacterQuestionnaire,
)
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema
from backend.app.infra.llm.llm_client import LLMClient


class CharacterGenerationService:
    """根据玩家问卷、世界和模组生成角色草案。"""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def _prepare_payload(
        self,
        raw_payload: dict,
        questionnaire: CharacterQuestionnaire,
    ) -> dict:
        normalized = normalize_character_payload(raw_payload)
        normalized.setdefault(
            "id",
            f"char_{questionnaire.case_id}_{questionnaire.player_id}",
        )
        normalized.setdefault("name", questionnaire.name_hint or questionnaire.player_id)
        normalized.setdefault("identity", questionnaire.identity_answer)
        normalized.setdefault("module_motivation", questionnaire.motivation_answer)
        if "concept" not in normalized:
            normalized["concept"] = (
                f"{questionnaire.identity_answer}。"
                f"{questionnaire.motivation_answer[:40]}"
            )
        return normalized

    async def generate(
        self,
        questionnaire: CharacterQuestionnaire,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
    ) -> CharacterGenerationOutput:
        system_prompt = load_prompt("character_generation.md")
        user_prompt = json.dumps(
            {
                "questionnaire": questionnaire.model_dump(mode="json"),
                "world": world.model_dump(mode="json"),
                "module": module.model_dump(mode="json"),
                "ruleset": ruleset.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        )
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
        )
        character = CharacterSheetSchema.model_validate(
            self._prepare_payload(raw_payload, questionnaire)
        )
        character = character.model_copy(update={"source": ArtifactSource.LLM})
        return CharacterGenerationOutput(character=character, raw_text=raw_text)

    async def repair(
        self,
        questionnaire: CharacterQuestionnaire,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
        broken_character: CharacterSheetSchema,
        review_summary: dict,
    ) -> CharacterGenerationOutput:
        system_prompt = load_prompt("character_repair.md")
        user_prompt = json.dumps(
            {
                "questionnaire": questionnaire.model_dump(mode="json"),
                "world": world.model_dump(mode="json"),
                "module": module.model_dump(mode="json"),
                "ruleset": ruleset.model_dump(mode="json"),
                "character": broken_character.model_dump(mode="json"),
                "review_summary": review_summary,
                "target_review_result": "approved",
            },
            ensure_ascii=False,
            indent=2,
        )
        raw_payload, raw_text = await self.llm_client.generate_json_dict(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,
        )
        character = CharacterSheetSchema.model_validate(
            self._prepare_payload(raw_payload, questionnaire)
        )
        character = character.model_copy(update={"source": ArtifactSource.LLM})
        return CharacterGenerationOutput(character=character, raw_text=raw_text)
