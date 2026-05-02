from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.schemas.common import BaseArtifact


class ClueLink(BaseModel):
    """线索与秘密之间的关联关系。"""

    model_config = ConfigDict(extra="forbid")

    clue_id: str = Field(description="线索自身的唯一标识。")
    target_secret_id: str = Field(description="该线索最终指向的秘密标识。")
    location_id: str | None = Field(default=None, description="该线索主要出现的地点标识。")
    fallback_clue_ids: list[str] = Field(
        default_factory=list,
        description="该线索错过后可替代的线索 id 列表。",
    )


class ModuleBlueprintSchema(BaseArtifact):
    """一场模组的可运行蓝图。"""

    model_config = ConfigDict(extra="forbid")

    world_id: str = Field(description="该模组归属的世界 id。")
    name: str = Field(description="模组名称。")
    player_count_min: int = Field(ge=1, le=8, description="推荐最少玩家人数。")
    player_count_max: int = Field(ge=1, le=8, description="推荐最多玩家人数。")
    duration_minutes: int = Field(ge=30, le=480, description="推荐游玩时长，单位分钟。")
    opening_hook: str = Field(description="玩家进入本模组的开场钩子。")
    core_secret: str = Field(description="模组核心秘密，AI 在运行中不得随意篡改。")
    major_conflict: str = Field(description="本模组的主要冲突。")
    required_npcs: list[str] = Field(min_length=1, description="必须出现的关键 NPC id 列表。")
    key_locations: list[str] = Field(min_length=1, description="关键地点 id 列表。")
    key_clues: list[ClueLink] = Field(min_length=1, description="关键线索及其指向关系。")
    threat_clock_id: str = Field(description="关联的威胁倒计时 id。")
    endings: dict[str, str] = Field(description="结局定义，至少包含 good、partial、bad。")
    ai_do_not_change: list[str] = Field(
        min_length=1,
        description="AI 运行时绝对不能改动的事实列表。",
    )
    ai_freedom_level: Literal["conservative", "standard", "high"] = Field(
        description="AI 的发挥自由度档位。"
    )

    @model_validator(mode="after")
    def validate_module_ranges(self) -> "ModuleBlueprintSchema":
        if self.player_count_min > self.player_count_max:
            raise ValueError("player_count_min cannot be greater than player_count_max")
        required_endings = {"good", "partial", "bad"}
        if not required_endings.issubset(self.endings):
            missing = required_endings - set(self.endings)
            raise ValueError(f"missing endings: {sorted(missing)}")
        return self
