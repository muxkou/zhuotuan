from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.ruleset import (
    RuleSetSchema,
    validate_attributes,
    validate_skill_budget,
)


class CharacterRulesValidator:
    """检查角色是否满足阶段一轻规则和基础必填要求。"""

    def validate(
        self,
        character: CharacterSheetSchema,
        ruleset: RuleSetSchema,
    ) -> ValidationReport:
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        required_fields = (
            "name",
            "identity",
            "concept",
            "module_motivation",
        )
        for field_name in required_fields:
            value = getattr(character, field_name)
            if not isinstance(value, str) or not value.strip():
                hard_errors.append(
                    ErrorItem(
                        code="missing_required_field",
                        message=f"{field_name} is required for a usable character sheet",
                        field_path=field_name,
                        severity="error",
                        suggestion=f"fill the {field_name} field with a specific answer",
                    )
                )

        if not character.personality_tags:
            hard_errors.append(
                ErrorItem(
                    code="missing_personality_tags",
                    message="personality_tags cannot be empty",
                    field_path="personality_tags",
                    severity="error",
                    suggestion="add at least one clear personality tag",
                )
            )

        if not character.strengths:
            hard_errors.append(
                ErrorItem(
                    code="missing_strengths",
                    message="strengths cannot be empty",
                    field_path="strengths",
                    severity="error",
                    suggestion="add at least one useful strength for play",
                )
            )

        if not character.weaknesses:
            hard_errors.append(
                ErrorItem(
                    code="missing_weaknesses",
                    message="weaknesses cannot be empty",
                    field_path="weaknesses",
                    severity="error",
                    suggestion="add at least one weakness for drama and balance",
                )
            )

        if not character.fears:
            hard_errors.append(
                ErrorItem(
                    code="missing_fears",
                    message="fears cannot be empty",
                    field_path="fears",
                    severity="error",
                    suggestion="add at least one fear that can be used in play",
                )
            )

        hard_errors.extend(validate_attributes(character.attributes))
        hard_errors.extend(validate_skill_budget(character.skills))

        total_attributes = sum(character.attributes.model_dump().values())
        total_skills = sum(character.skills.model_dump().values())
        if total_attributes <= -1:
            warnings.append(
                ErrorItem(
                    code="low_attribute_budget",
                    message=(
                        "attribute budget is very low and may make the "
                        "character frustrating to play"
                    ),
                    field_path="attributes",
                    severity="warning",
                    suggestion="shift one or two points into the character's core strengths",
                )
            )
        if total_skills == 0:
            warnings.append(
                ErrorItem(
                    code="no_skill_specialization",
                    message="the character has no highlighted skills",
                    field_path="skills",
                    severity="warning",
                    suggestion="give the character at least one visible area of expertise",
                )
            )

        if character.secret is None:
            suggestions.append("可以补一条个人秘密，方便 Session 0 绑定和后续戏剧推进。")

        status = (
            ValidationStatus.FAIL
            if hard_errors
            else ValidationStatus.WARN
            if warnings
            else ValidationStatus.PASS
        )
        return ValidationReport(
            status=status,
            hard_errors=hard_errors,
            warnings=warnings,
            suggestions=suggestions,
            metrics={
                "attribute_total": total_attributes,
                "skill_total": total_skills,
                "ruleset_name": ruleset.name,
            },
        )
