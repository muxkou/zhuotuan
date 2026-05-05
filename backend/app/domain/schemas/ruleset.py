from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.schemas.common import BaseArtifact, ErrorItem


class AttributeScore(BaseModel):
    """角色五维属性。"""

    model_config = ConfigDict(extra="forbid")

    physique: int = Field(ge=0, le=3, description="体魄，表示力量、耐力和近身行动能力。")
    agility: int = Field(ge=0, le=3, description="机敏，表示反应、潜行、闪避等能力。")
    mind: int = Field(ge=0, le=3, description="心智，表示调查、推理、知识理解能力。")
    willpower: int = Field(ge=0, le=3, description="意志，表示抗压、抵抗恐惧、坚持能力。")
    social: int = Field(ge=0, le=3, description="社交，表示说服、伪装、威胁、共情能力。")


class SkillBonus(BaseModel):
    """角色在常用技能上的额外修正值。"""

    model_config = ConfigDict(extra="forbid")

    investigation: int = Field(default=0, ge=0, le=3, description="调查技能修正。")
    negotiation: int = Field(default=0, ge=0, le=3, description="交涉技能修正。")
    stealth: int = Field(default=0, ge=0, le=3, description="潜行技能修正。")
    combat: int = Field(default=0, ge=0, le=3, description="战斗技能修正。")
    medicine: int = Field(default=0, ge=0, le=3, description="医治技能修正。")
    occult: int = Field(default=0, ge=0, le=3, description="神秘学或民俗知识修正。")
    craft: int = Field(default=0, ge=0, le=3, description="技艺或手工相关修正。")
    survival: int = Field(default=0, ge=0, le=3, description="生存技能修正。")


class RuleSetSchema(BaseArtifact):
    """一套可运行规则的静态定义。"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="规则名称，例如原创轻规则。")
    description: str = Field(description="规则的简短说明。")
    dice_formula: Literal["2d6"] = Field(description="当前规则使用的骰点公式。")
    difficulty_bands: dict[str, int] = Field(description="难度档位到目标值的映射。")
    attributes: list[str] = Field(min_length=1, description="本规则支持的属性列表。")
    skills: list[str] = Field(min_length=1, description="本规则支持的技能列表。")
    resource_rules: dict[str, int | str] = Field(description="生命、精神、压力等资源的初始规则。")

    @model_validator(mode="after")
    def validate_difficulty_bands(self) -> "RuleSetSchema":
        required_bands = {"easy", "standard", "hard"}
        if not required_bands.issubset(self.difficulty_bands):
            missing = required_bands - set(self.difficulty_bands)
            raise ValueError(f"missing difficulty bands: {sorted(missing)}")
        return self


def validate_attributes(
    attrs: AttributeScore,
    budget_min: int = 0,
    budget_max: int = 4,
) -> list[ErrorItem]:
    total = attrs.physique + attrs.agility + attrs.mind + attrs.willpower + attrs.social
    errors: list[ErrorItem] = []
    if total < budget_min or total > budget_max:
        errors.append(
            ErrorItem(
                code="attribute_budget_out_of_range",
                message=(
                    f"attribute total {total} is outside allowed range "
                    f"[{budget_min}, {budget_max}]"
                ),
                field_path="attributes",
                severity="error",
                suggestion="adjust attribute points to fit the starter ruleset budget",
            )
        )
    return errors


def validate_skill_budget(
    skills: SkillBonus | dict[str, int],
    budget_max: int = 6,
) -> list[ErrorItem]:
    dumped_skills = skills.model_dump() if isinstance(skills, SkillBonus) else skills
    total = sum(dumped_skills.values())
    errors: list[ErrorItem] = []
    if total > budget_max:
        errors.append(
            ErrorItem(
                code="skill_budget_exceeded",
                message=f"skill total {total} exceeds allowed maximum {budget_max}",
                field_path="skills",
                severity="error",
                suggestion="reduce skill bonuses to match the phase 1 starter budget",
            )
        )
    return errors
