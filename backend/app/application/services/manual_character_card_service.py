from backend.app.application.services.response_normalizers import normalize_character_payload
from backend.app.domain.enums.game import ArtifactSource
from backend.app.domain.schemas.character import CharacterSheetSchema, ManualCharacterCardInput
from backend.app.domain.schemas.world import WorldSchema
from backend.app.domain.value_objects.id_factory import generate_id


class ManualCharacterCardService:
    """把玩家手动填写的车卡输入转换为可审核的角色卡。"""

    def build_character(
        self,
        manual_input: ManualCharacterCardInput,
        world: WorldSchema,
    ) -> CharacterSheetSchema:
        payload = manual_input.model_dump(mode="json")
        raw_attributes = payload.pop("attributes")
        payload["attributes"] = raw_attributes
        payload["extra_attributes"] = {}
        payload.pop("case_id", None)
        payload.pop("player_id", None)
        payload["id"] = generate_id("char")
        normalized = normalize_character_payload(payload)
        character = CharacterSheetSchema.model_validate(normalized)
        return character.model_copy(update={"source": ArtifactSource.HUMAN})
