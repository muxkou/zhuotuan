from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.world import WorldSchema

FORBIDDEN_POWER_KEYWORDS = (
    "读心",
    "预知未来",
    "时间停止",
    "瞬间移动",
    "起死回生",
    "神明化身",
    "不死之身",
    "操控所有人",
)

WORLD_WARNING_KEYWORDS = (
    "职业驱魔师",
    "超能力特工",
    "天选之子",
)


class CharacterWorldValidator:
    """检查角色是否明显违反世界观边界。"""

    def validate(
        self,
        character: CharacterSheetSchema,
        world: WorldSchema,
    ) -> ValidationReport:
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        searchable_segments = [
            character.identity,
            character.concept,
            character.secret or "",
            *character.strengths,
            *character.inventory,
        ]
        searchable_text = "\n".join(searchable_segments)

        for keyword in FORBIDDEN_POWER_KEYWORDS:
            if keyword in searchable_text:
                hard_errors.append(
                    ErrorItem(
                        code="forbidden_supernatural_power",
                        message=f"character includes world-breaking power: {keyword}",
                        field_path="concept",
                        severity="error",
                        suggestion=(
                            "remove the direct supernatural power and convert it "
                            "into rumor, skill, or trauma"
                        ),
                    )
                )

        for keyword in WORLD_WARNING_KEYWORDS:
            if keyword in searchable_text:
                warnings.append(
                    ErrorItem(
                        code="world_tone_mismatch",
                        message=(
                            "character concept may be too explicit or heroic "
                            f"for the current world tone: {keyword}"
                        ),
                        field_path="identity",
                        severity="warning",
                        suggestion="make the identity more grounded and ambiguous",
                    )
                )

        if character.identity not in world.recommended_roles:
            suggestions.append(
                "当前身份不在世界推荐身份里，建议确认它是否仍方便切入线索和与其他玩家协作。"
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
                "recommended_role_match": int(character.identity in world.recommended_roles),
                "taboo_count": len(world.taboos),
            },
        )
