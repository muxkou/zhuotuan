from pydantic import ConfigDict, Field, model_validator

from backend.app.domain.schemas.common import BaseArtifact
from backend.app.domain.schemas.ruleset import AttributeScore, SkillBonus


class CharacterSheetSchema(BaseArtifact):
    """玩家角色卡定义。"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="角色姓名。")
    identity: str = Field(description="角色身份，例如记者、医生、巡警。")
    concept: str = Field(description="一句话角色概念。")
    personality_tags: list[str] = Field(min_length=1, description="角色性格关键词。")
    module_motivation: str = Field(description="角色参与当前模组的直接动机。")
    attributes: AttributeScore = Field(description="角色属性面板。")
    extra_attributes: dict[str, int] = Field(
        default_factory=dict,
        description="世界特有的额外属性，键必须在世界车卡规范中定义。",
    )
    skills: SkillBonus = Field(description="角色技能修正。")
    strengths: list[str] = Field(min_length=1, description="角色优势或擅长点。")
    weaknesses: list[str] = Field(min_length=1, description="角色弱点。")
    fears: list[str] = Field(min_length=1, description="角色恐惧点。")
    secret: str | None = Field(default=None, description="角色个人秘密，可选。")
    relationships: list[dict[str, str]] = Field(
        default_factory=list,
        description="与其他角色或 NPC 的关系描述。",
    )
    inventory: list[str] = Field(default_factory=list, description="初始持有物品列表。")

    @model_validator(mode="after")
    def validate_character_motivation(self) -> "CharacterSheetSchema":
        if len(self.module_motivation.strip()) < 6:
            raise ValueError("module_motivation should be descriptive enough for session 0 binding")
        return self
