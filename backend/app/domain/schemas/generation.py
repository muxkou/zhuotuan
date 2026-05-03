from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.schemas.common import ValidationReport
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.world import WorldSchema


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
