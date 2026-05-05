from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ValidationReport
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.world import CharacterCreationProfile, WorldSchema


class QuickStartInput(BaseModel):
    """快速开团的结构化输入。"""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="本次快速开团案例 id，用于落盘与回放。")
    genre: str = Field(description="题材，例如中式怪谈、都市异闻、武侠悬疑。")
    duration_minutes: int = Field(ge=30, le=480, description="期望总时长，单位分钟。")
    player_count: int = Field(ge=1, le=8, description="预期玩家人数。")
    tone: list[str] = Field(min_length=1, description="氛围关键词。")
    inspiration: str | None = Field(default=None, description="一句话灵感，可选。")
    horror_level: Literal["low", "medium", "high"] = Field(description="恐怖强度。")
    combat_ratio: Literal["low", "medium", "high"] = Field(default="low", description="战斗占比。")
    investigation_ratio: Literal["low", "medium", "high"] = Field(
        default="high",
        description="调查占比。",
    )


class WorldGenerationOutput(BaseModel):
    """世界生成服务的输出包装。"""

    model_config = ConfigDict(extra="forbid")

    world: WorldSchema
    raw_text: str | None = Field(default=None, description="模型原始输出，便于调试。")


class CharacterCreationProfileGenerationOutput(BaseModel):
    """世界车卡规则生成服务的输出包装。"""

    model_config = ConfigDict(extra="forbid")

    profile: CharacterCreationProfile
    raw_text: str | None = Field(default=None, description="模型原始输出，便于调试。")


class ModuleGenerationOutput(BaseModel):
    """模组生成服务的输出包装。"""

    model_config = ConfigDict(extra="forbid")

    module: ModuleBlueprintSchema
    raw_text: str | None = Field(default=None, description="模型原始输出，便于调试。")


class ModuleGenerationRunOutput(BaseModel):
    """模组生成完整流程的输出，包括校验和可选修补。"""

    model_config = ConfigDict(extra="forbid")

    module: ModuleBlueprintSchema
    initial_report: "ModulePlayabilityReport"
    final_report: "ModulePlayabilityReport"
    repair_attempted: bool = Field(description="本次流程是否触发过 repair pass。")
    repaired: bool = Field(description="repair 后最终模组对象是否替换了初始生成对象。")
    initial_raw_text: str | None = Field(default=None, description="第一次生成时的原始模型输出。")
    repair_raw_text: str | None = Field(default=None, description="repair pass 的原始模型输出。")


class ModulePlayabilityReport(ValidationReport):
    """模组可运行性校验报告。"""

    model_config = ConfigDict(extra="forbid")

    missing_core_fields: list[str] = Field(default_factory=list, description="缺失的关键字段名称。")
    uncovered_secret_ids: list[str] = Field(
        default_factory=list,
        description="未被足够线索覆盖的秘密标识。",
    )
    clue_path_count: int = Field(default=0, description="当前指向核心秘密的关键线索数量。")


class CharacterQuestionnaire(BaseModel):
    """玩家填写的角色问卷输入。"""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="本次角色创建绑定的 case id。")
    player_id: str = Field(description="玩家唯一标识，用于区分不同玩家问卷。")
    name_hint: str | None = Field(default=None, description="玩家偏好的姓名提示，可选。")
    identity_answer: str = Field(description="玩家想扮演的身份回答。")
    motivation_answer: str = Field(description="玩家给出的参团动机回答。")
    specialty_answer: str = Field(description="玩家希望角色擅长的方向。")
    fear_answer: str = Field(description="玩家希望角色害怕或在意的事物。")
    relationship_answer: str | None = Field(
        default=None,
        description="玩家期望的初始关系或绑定对象，可选。",
    )
    secret_answer: str | None = Field(default=None, description="玩家接受的个人秘密线索，可选。")


class CharacterGenerationOutput(BaseModel):
    """角色生成服务的输出包装。"""

    model_config = ConfigDict(extra="forbid")

    character: CharacterSheetSchema
    raw_text: str | None = Field(default=None, description="模型原始输出，便于调试。")


class CharacterReviewReport(ValidationReport):
    """角色审核后的统一报告。"""

    model_config = ConfigDict(extra="forbid")

    review_result: Literal["approved", "needs_revision", "warning", "enhance"] = Field(
        description="面向上层流程的审核结论。"
    )
    normalized_character: CharacterSheetSchema | None = Field(
        default=None,
        description="审核后可继续向下游传递的角色对象。",
    )
    blocking_reasons: list[str] = Field(
        default_factory=list,
        description="阻塞通过的核心原因摘要。",
    )
    revision_suggestions: list[str] = Field(
        default_factory=list,
        description="建议玩家或修补流程优先处理的修改建议。",
    )
    queue_position: int | None = Field(
        default=None,
        description="该角色在当前房间审核队列中的位置。",
    )
    roster_conflicts: list[str] = Field(
        default_factory=list,
        description="与已通过角色 roster 的冲突摘要。",
    )


class CharacterGenerationRunOutput(BaseModel):
    """角色生成完整流程的输出，包括审核和可选修补。"""

    model_config = ConfigDict(extra="forbid")

    character: CharacterSheetSchema
    initial_review_report: CharacterReviewReport
    final_review_report: CharacterReviewReport
    repair_attempted: bool = Field(description="本次流程是否触发过 repair pass。")
    repaired: bool = Field(description="repair 后最终角色对象是否替换了初始角色对象。")
    initial_raw_text: str | None = Field(default=None, description="第一次生成时的原始模型输出。")
    repair_raw_text: str | None = Field(default=None, description="repair pass 的原始模型输出。")
