from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.ruleset import (
    RuleSetSchema,
    validate_attributes,
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

        total_attributes = sum(character.attributes.model_dump().values()) + sum(
            character.extra_attributes.values()
        )
        total_skills = sum(character.skills.values())
        if total_attributes <= 1:
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
        maxed_skill_count = sum(1 for value in character.skills.values() if value >= 2)
        if maxed_skill_count >= 3:
            warnings.append(
                ErrorItem(
                    code="over_concentrated_skills",
                    message="the character has too many proficient skills for the phase-1 baseline",
                    field_path="skills",
                    severity="warning",
                    suggestion="lower one of the maxed skills or spread the focus more naturally",
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
