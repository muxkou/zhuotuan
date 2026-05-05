from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.schemas.common import BaseArtifact
from backend.app.domain.schemas.ruleset import AttributeScore


class ManualCharacterCardInput(BaseModel):
    """玩家手动填写并提交审核的车卡输入。"""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="本次角色创建绑定的 case id。")
    player_id: str = Field(description="玩家唯一标识，用于排队审核和追踪。")
    name: str = Field(description="角色姓名。")
    identity: str = Field(description="角色身份，例如记者、医生、巡警。")
    concept: str = Field(description="一句话角色概念。")
    personality_tags: list[str] = Field(min_length=1, description="角色性格关键词。")
    module_motivation: str = Field(description="角色参与当前模组的直接动机。")
    attributes: dict[str, int] = Field(
        description="玩家填写的全部属性，键必须来自世界车卡规范。",
    )
    skills: dict[str, int] = Field(
        default_factory=dict,
        description="玩家填写的技能点，键必须来自世界技能表，值只能为 0、1、2。",
    )
    strengths: list[str] = Field(min_length=1, description="角色优势或擅长点。")
    weaknesses: list[str] = Field(min_length=1, description="角色弱点。")
    fears: list[str] = Field(min_length=1, description="角色恐惧点。")
    secret: str | None = Field(default=None, description="角色个人秘密，可选。")
    relationships: list[dict[str, str]] = Field(
        default_factory=list,
        description="与其他角色或 NPC 的关系描述。",
    )
    inventory: list[str] = Field(default_factory=list, description="初始持有物品列表。")


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
    skills: dict[str, int] = Field(
        default_factory=dict,
        description="角色技能点，键来自世界技能表，值固定为 0=不会、1=会、2=精通。",
    )
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
        for key, value in self.skills.items():
            if value < 0 or value > 2:
                raise ValueError(f"skill {key} must be between 0 and 2")
        return self
