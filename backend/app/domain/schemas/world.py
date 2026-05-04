from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.schemas.common import BaseArtifact


class AttributeSemanticBand(BaseModel):
    """属性数值区间的语义解释。"""

    model_config = ConfigDict(extra="forbid")

    min_value: int = Field(ge=0, description="该语义区间的最小值。")
    max_value: int = Field(ge=0, description="该语义区间的最大值。")
    summary: str = Field(description="该数值区间代表的角色表现概述。")
    examples: list[str] = Field(default_factory=list, description="可选的行为示例。")


class AttributeDefinition(BaseModel):
    """车卡时允许使用的一项属性定义。"""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(description="属性英文 key，例如 physique、mind、spirit_sensitivity。")
    label: str = Field(description="属性显示名称。")
    description: str = Field(description="属性含义说明。")
    min_value: int = Field(ge=0, description="该属性允许的最小值。")
    max_value: int = Field(ge=0, description="该属性允许的最大值。")
    semantic_bands: list[AttributeSemanticBand] = Field(
        min_length=1,
        description="该属性每个数值区间的语义说明。",
    )
    is_core: bool = Field(default=True, description="是否属于当前世界默认的基础属性。")

    @model_validator(mode="after")
    def validate_semantic_bands(self) -> "AttributeDefinition":
        for band in self.semantic_bands:
            if band.min_value < self.min_value or band.max_value > self.max_value:
                raise ValueError(f"semantic band for {self.key} exceeds attribute range")
            if band.min_value > band.max_value:
                raise ValueError(f"semantic band for {self.key} has invalid range")
        return self


class SpecialStatusDefinition(BaseModel):
    """世界中的特殊状态定义，供后续 AI KP 与运行时约束使用。"""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(description="特殊状态 key，例如 charmed、polluted。")
    label: str = Field(description="特殊状态名称。")
    description: str = Field(description="状态本身的解释。")
    trigger_sources: list[str] = Field(min_length=1, description="常见触发来源。")
    behavioral_constraints: list[str] = Field(min_length=1, description="状态存在时的行为限制。")
    recovery_hints: list[str] = Field(default_factory=list, description="缓解或解除该状态的提示。")


class CharacterCreationProfile(BaseModel):
    """一个世界下的车卡规范。"""

    model_config = ConfigDict(extra="forbid")

    base_attributes: list[AttributeDefinition] = Field(
        min_length=1,
        description="当前世界默认采用的基础属性。",
    )
    world_specific_attributes: list[AttributeDefinition] = Field(
        default_factory=list,
        description="该世界额外引入的特殊属性。",
    )
    total_attribute_budget_min: int = Field(ge=0, description="角色总属性点允许的最小预算。")
    total_attribute_budget_max: int = Field(ge=0, description="角色总属性点允许的最大预算。")
    identity_guidelines: list[str] = Field(
        default_factory=list,
        description="推荐的身份与人设方向说明。",
    )
    forbidden_character_elements: list[str] = Field(
        default_factory=list,
        description="世界明确不允许的车卡元素。",
    )

    @property
    def all_attributes(self) -> list[AttributeDefinition]:
        return [*self.base_attributes, *self.world_specific_attributes]


def _base_attribute_definition(
    key: str,
    label: str,
    description: str,
    low_summary: str,
    mid_summary: str,
    high_summary: str,
) -> AttributeDefinition:
    return AttributeDefinition(
        key=key,
        label=label,
        description=description,
        min_value=0,
        max_value=3,
        semantic_bands=[
            AttributeSemanticBand(
                min_value=0,
                max_value=0,
                summary=low_summary,
                examples=["在该维度明显吃力。"],
            ),
            AttributeSemanticBand(
                min_value=1,
                max_value=2,
                summary=mid_summary,
                examples=["可以完成普通人的常规表现。"],
            ),
            AttributeSemanticBand(
                min_value=3,
                max_value=3,
                summary=high_summary,
                examples=["在这一维度属于非常突出。"],
            ),
        ],
        is_core=True,
    )


def default_character_creation_profile() -> CharacterCreationProfile:
    return CharacterCreationProfile(
        base_attributes=[
            _base_attribute_definition(
                key="physique",
                label="体魄",
                description="力量、耐力、负重、近身动作能力。",
                low_summary="体魄偏弱，长时间奔跑、负重或对抗会非常困难。",
                mid_summary="体魄正常，能应对普通人的常见体能挑战。",
                high_summary="体魄出众，近身对抗和耐力表现明显优于常人。",
            ),
            _base_attribute_definition(
                key="agility",
                label="机敏",
                description="反应、平衡、闪避、潜行、手上动作。",
                low_summary="动作笨拙，反应偏慢，细致动作和闪避较难。",
                mid_summary="机敏正常，可以处理普通移动与潜行动作。",
                high_summary="机敏出众，适合潜行、闪避与细密动作。",
            ),
            _base_attribute_definition(
                key="mind",
                label="心智",
                description="理解力、推理、观察、调查、知识整合。",
                low_summary="理解复杂信息较慢，难以快速读懂隐含关系。",
                mid_summary="能正常理解、分析并处理调查信息。",
                high_summary="推理和洞察非常强，能快速抓住关键矛盾。",
            ),
            _base_attribute_definition(
                key="willpower",
                label="意志",
                description="抗压、忍耐、抵抗恐惧、坚持目标。",
                low_summary="容易在恐惧、痛苦或诱惑面前动摇。",
                mid_summary="具备普通人的承压与坚持能力。",
                high_summary="在恐惧、迷惑和精神压迫下依然能保持清醒。",
            ),
            _base_attribute_definition(
                key="social",
                label="社交",
                description="说服、伪装、威吓、安抚、共情与人情判断。",
                low_summary="不善表达或读人，交流中经常处于下风。",
                mid_summary="社交能力正常，能完成常规沟通与劝说。",
                high_summary="在洞察人心、建立关系和影响他人上很有优势。",
            ),
        ],
        total_attribute_budget_min=0,
        total_attribute_budget_max=4,
        identity_guidelines=[
            "优先选择能自然卷入调查、求助、护送、追凶、守秘的普通人身份。",
            "角色应保留缺点和代价，不建议直接写成全能英雄或超能力者。",
        ],
        forbidden_character_elements=[
            "明确可控的强超自然能力",
            "直接知道模组核心真相",
            "完全拒绝与队友合作的人设",
        ],
    )


def default_special_status_catalog() -> list[SpecialStatusDefinition]:
    return [
        SpecialStatusDefinition(
            key="bewildered",
            label="迷惑",
            description="角色被异常现象、怪物或神话信息扰乱判断。",
            trigger_sources=["直视异常本体", "长时间接触污染物", "听闻不可承受的真相"],
            behavioral_constraints=[
                "短时间内难以分辨真伪线索",
                "在 AI KP 演绎中应出现迟疑、误认或错误联想",
            ],
            recovery_hints=["脱离污染源", "获得同伴提醒", "完成一次稳定情绪的短暂休整"],
        ),
        SpecialStatusDefinition(
            key="haunted",
            label="侵扰",
            description="角色持续受到异常注视、低语或旧案残响干扰。",
            trigger_sources=["靠近核心异常地点", "持有被污染遗物"],
            behavioral_constraints=[
                "休息和独处时更容易触发幻听、梦魇或回忆闪回",
                "AI KP 不应把该状态直接演成完全失控",
            ],
            recovery_hints=["找到状态来源", "完成净化或安抚仪式"],
        ),
    ]


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
    character_creation_profile: CharacterCreationProfile = Field(
        default_factory=default_character_creation_profile,
        description="该世界下的车卡规范，包括属性定义、预算和禁用元素。",
    )
    special_status_catalog: list[SpecialStatusDefinition] = Field(
        default_factory=default_special_status_catalog,
        description="该世界可能出现的特殊状态定义。",
    )
