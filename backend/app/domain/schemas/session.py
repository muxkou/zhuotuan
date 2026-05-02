from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.enums.game import ActorType, ResolutionGrade
from backend.app.domain.schemas.common import BaseArtifact


class TurnRecordSchema(BaseModel):
    """单个游玩回合的记录。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="回合记录唯一标识。")
    turn_index: int = Field(ge=0, description="当前回合序号，从 0 开始递增。")
    actor_type: ActorType = Field(description="发起本回合动作的主体类型。")
    actor_id: str = Field(description="发起本回合动作的主体 id。")
    player_input: str | None = Field(default=None, description="玩家原始输入文本。")
    interpreted_action_type: str | None = Field(default=None, description="系统解析出的行动类型。")
    roll_required: bool = Field(description="本回合是否需要掷骰判定。")
    roll_formula: str | None = Field(default=None, description="若需判定，使用的骰点公式。")
    roll_total: int | None = Field(default=None, description="最终掷骰总值，含修正。")
    difficulty: int | None = Field(default=None, description="本次判定目标难度值。")
    resolution_grade: ResolutionGrade | None = Field(
        default=None,
        description="本次判定得到的结果等级。",
    )
    consequence_summary: str = Field(description="本回合后果的摘要描述。")
    state_delta: dict[str, Any] = Field(description="本回合对运行时状态造成的变化。")


class ClueStateSchema(BaseModel):
    """运行时线索状态。"""

    model_config = ConfigDict(extra="forbid")

    clue_id: str = Field(description="线索 id。")
    status: str = Field(description="线索当前状态，例如 undiscovered、discovered、verified。")
    discovered_by: list[str] = Field(default_factory=list, description="发现该线索的角色 id 列表。")
    public_notes: list[str] = Field(
        default_factory=list,
        description="允许玩家公开看到的线索备注。",
    )


class NpcStateSchema(BaseModel):
    """运行时 NPC 状态。"""

    model_config = ConfigDict(extra="forbid")

    npc_id: str = Field(description="NPC id。")
    attitude: str = Field(description="NPC 当前对玩家的态度。")
    current_status: str = Field(description="NPC 当前状态，例如 watchful、injured、missing。")
    public_summary: str = Field(description="允许玩家侧看到的 NPC 状态摘要。")


class CharacterRuntimeStateSchema(BaseModel):
    """角色在运行时的资源和状态。"""

    model_config = ConfigDict(extra="forbid")

    character_id: str = Field(description="角色 id。")
    hp: int = Field(description="当前生命值或身体状态数值。")
    mp: int = Field(description="当前精神值或心智资源数值。")
    stress: int = Field(description="当前压力值。")
    injuries: list[str] = Field(default_factory=list, description="角色当前伤势列表。")
    flags: list[str] = Field(default_factory=list, description="角色当前特殊状态标记。")


class ThreatClockStateSchema(BaseModel):
    """威胁倒计时的运行时进度。"""

    model_config = ConfigDict(extra="forbid")

    threat_clock_id: str = Field(description="威胁倒计时 id。")
    current_stage: int = Field(ge=0, description="当前已经推进到的阶段序号。")
    stage_label: str = Field(description="当前阶段的人类可读名称。")
    triggered_events: list[str] = Field(
        default_factory=list,
        description="已经触发过的倒计时事件列表。",
    )


class SessionReportSchema(BaseModel):
    """单次会话结束后的结构化战报。"""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="战报标题。")
    summary: str = Field(description="本场摘要。")
    key_events: list[str] = Field(description="本场关键事件列表。")
    discovered_clues: list[str] = Field(description="本场新发现或确认的线索。")
    unresolved_questions: list[str] = Field(description="本场结束后仍未解决的问题。")
    character_changes: list[str] = Field(description="角色状态变化摘要。")
    npc_changes: list[str] = Field(description="NPC 状态变化摘要。")
    threat_clock_changes: list[str] = Field(description="威胁倒计时变化摘要。")
    next_session_suggestions: list[str] = Field(description="下场开局建议。")


class SessionSnapshotSchema(BaseArtifact):
    """一次会话结束后保存的运行时快照。"""

    model_config = ConfigDict(extra="forbid")

    table_id: str = Field(description="当前跑团实例 id。")
    session_id: str = Field(description="当前会话 id。")
    clue_states: list[ClueStateSchema] = Field(
        default_factory=list,
        description="当前已知线索的运行时状态列表。",
    )
    npc_states: list[NpcStateSchema] = Field(
        default_factory=list,
        description="当前 NPC 运行时状态列表。",
    )
    character_states: list[CharacterRuntimeStateSchema] = Field(
        default_factory=list,
        description="当前玩家角色运行时状态列表。",
    )
    threat_clock_state: ThreatClockStateSchema = Field(description="当前威胁倒计时状态。")
    unresolved_questions: list[str] = Field(
        default_factory=list,
        description="当前仍未解决的关键问题。",
    )
