from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.world import WorldSchema


class CharacterWorldProfileValidator:
    """检查角色是否满足世界定义的车卡约束。"""

    def validate(
        self,
        character: CharacterSheetSchema,
        world: WorldSchema,
    ) -> ValidationReport:
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        profile = world.character_creation_profile
        attribute_defs = {
            definition.key: definition
            for definition in profile.all_attributes
        }

        all_character_attributes = {
            **character.attributes.model_dump(),
            **character.extra_attributes,
        }
        for key, value in all_character_attributes.items():
            attribute_def = attribute_defs.get(key)
            if attribute_def is None:
                hard_errors.append(
                    ErrorItem(
                        code="unknown_world_attribute",
                        message=f"attribute {key} is not allowed by the world creation profile",
                        field_path=f"attributes.{key}",
                        severity="error",
                        suggestion="remove the attribute or add it to the world creation profile",
                    )
                )
                continue
            if value < attribute_def.min_value or value > attribute_def.max_value:
                hard_errors.append(
                    ErrorItem(
                        code="attribute_out_of_world_range",
                        message=(
                            f"attribute {key}={value} is outside world range "
                            f"[{attribute_def.min_value}, {attribute_def.max_value}]"
                        ),
                        field_path=f"attributes.{key}",
                        severity="error",
                        suggestion="adjust the attribute to the world-defined range",
                    )
                )

        total_attribute_points = sum(all_character_attributes.values())
        if (
            total_attribute_points < profile.total_attribute_budget_min
            or total_attribute_points > profile.total_attribute_budget_max
        ):
            hard_errors.append(
                ErrorItem(
                    code="attribute_total_out_of_world_budget",
                    message=(
                        f"attribute total {total_attribute_points} is outside world budget "
                        "["
                        f"{profile.total_attribute_budget_min}, "
                        f"{profile.total_attribute_budget_max}]"
                    ),
                    field_path="attributes",
                    severity="error",
                    suggestion=(
                        "reallocate the character attributes to fit the world "
                        "creation budget"
                    ),
                )
            )

        skill_defs = {definition.key: definition for definition in profile.skills}
        for key, value in character.skills.items():
            if key not in skill_defs:
                hard_errors.append(
                    ErrorItem(
                        code="unknown_world_skill",
                        message=f"skill {key} is not allowed by the world creation profile",
                        field_path=f"skills.{key}",
                        severity="error",
                        suggestion="remove the skill or add it to the world skill list",
                    )
                )
                continue
            if value < 0 or value > 2:
                hard_errors.append(
                    ErrorItem(
                        code="skill_out_of_world_range",
                        message=f"skill {key}={value} must be between 0 and 2",
                        field_path=f"skills.{key}",
                        severity="error",
                        suggestion="set the skill to 0, 1 or 2",
                    )
                )

        total_skill_points = sum(character.skills.values())
        if total_skill_points > profile.total_skill_points:
            hard_errors.append(
                ErrorItem(
                    code="skill_total_out_of_world_budget",
                    message=(
                        f"skill total {total_skill_points} exceeds world budget "
                        f"{profile.total_skill_points}"
                    ),
                    field_path="skills",
                    severity="error",
                    suggestion="reduce skill points to fit the world creation budget",
                )
            )
        if not character.skills or total_skill_points == 0:
            warnings.append(
                ErrorItem(
                    code="no_skill_specialization",
                    message="the character has no highlighted skills",
                    field_path="skills",
                    severity="warning",
                    suggestion="give the character at least one visible area of expertise",
                )
            )

        searchable_text = "\n".join(
            [
                character.identity,
                character.concept,
                character.secret or "",
                *character.personality_tags,
                *character.strengths,
                *character.weaknesses,
            ]
        )
        for forbidden_element in profile.forbidden_character_elements:
            if forbidden_element and forbidden_element in searchable_text:
                warnings.append(
                    ErrorItem(
                        code="forbidden_character_element_hit",
                        message=(
                            "character text appears to directly include a forbidden world element: "
                            f"{forbidden_element}"
                        ),
                        field_path="concept",
                        severity="warning",
                        suggestion=(
                            "rewrite the relevant concept or secret to stay "
                            "within the world framing"
                        ),
                    )
                )

        if profile.identity_guidelines and character.identity not in world.recommended_roles:
            suggestions.append(
                "当前身份不在推荐身份中，建议确认它仍能自然切入本世界的调查或冲突。"
            )

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
                "world_attribute_count": len(attribute_defs),
                "character_attribute_total": total_attribute_points,
                "world_skill_count": len(skill_defs),
                "character_skill_total": total_skill_points,
                "world_status_count": len(world.special_status_catalog),
            },
        )
