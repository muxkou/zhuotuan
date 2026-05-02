from pydantic import ConfigDict, Field

from backend.app.domain.schemas.common import BaseArtifact


class WorldSchema(BaseArtifact):
    """可复用世界观定义。"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="世界名称。")
    tagline: str = Field(description="一句话介绍这个世界。")
    genre: str = Field(description="题材类型，例如中式怪谈调查。")
    era: str = Field(description="时代背景，例如架空近现代。")
    tone: list[str] = Field(min_length=1, description="整体氛围关键词。")
    public_rules: list[str] = Field(min_length=1, description="玩家默认知道的世界常识和规则。")
    hidden_rules: list[str] = Field(
        default_factory=list,
        description="仅系统或作者知道的隐藏世界规则。",
    )
    factions: list[str] = Field(min_length=1, description="世界中的主要势力。")
    common_locations: list[str] = Field(min_length=1, description="世界中常见或高频出现的地点。")
    taboos: list[str] = Field(min_length=1, description="世界中的禁忌或不可触碰事项。")
    recommended_roles: list[str] = Field(min_length=1, description="推荐玩家扮演的角色身份。")
    narration_style: dict[str, str | int] = Field(
        description="叙事风格参数，例如恐怖强度、节奏、对白风格。"
    )
