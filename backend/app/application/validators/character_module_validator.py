import re

from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.module import ModuleBlueprintSchema

DISENGAGED_MOTIVATION_KEYWORDS = (
    "路过",
    "没兴趣",
    "被迫",
    "随便看看",
    "不知道为什么",
)
ANTI_COOP_KEYWORDS = (
    "独狼",
    "拒绝合作",
    "背刺队友",
    "仇视所有人",
    "单独行动",
)
STOPWORDS = {
    "必须",
    "有关",
    "一个",
    "秘密",
    "真相",
    "进行",
    "正在",
    "他们",
    "我们",
    "因为",
}


def _extract_secret_keywords(text: str) -> set[str]:
    keywords: set[str] = set()
    for token in re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text):
        stripped = token.strip()
        if len(stripped) < 2 or stripped in STOPWORDS:
            continue
        keywords.add(stripped)
    return keywords


class CharacterModuleValidator:
    """检查角色是否会破坏模组体验或协作。"""

    def validate(
        self,
        character: CharacterSheetSchema,
        module: ModuleBlueprintSchema,
    ) -> ValidationReport:
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        motivation = character.module_motivation.strip()
        if len(motivation) < 8 or any(
            keyword in motivation for keyword in DISENGAGED_MOTIVATION_KEYWORDS
        ):
            hard_errors.append(
                ErrorItem(
                    code="weak_module_motivation",
                    message=(
                        "character lacks a strong enough motivation to join "
                        "and stay in the scenario"
                    ),
                    field_path="module_motivation",
                    severity="error",
                    suggestion=(
                        "rewrite the motivation so it clearly ties the "
                        "character to the opening hook or conflict"
                    ),
                )
            )

        cooperation_text = "\n".join(
            [
                *character.personality_tags,
                *character.weaknesses,
                character.concept,
            ]
        )
        if any(keyword in cooperation_text for keyword in ANTI_COOP_KEYWORDS):
            hard_errors.append(
                ErrorItem(
                    code="cooperation_breaker",
                    message="character concept makes party cooperation too difficult",
                    field_path="personality_tags",
                    severity="error",
                    suggestion=(
                        "keep the edge or trauma, but add a reason to trust "
                        "or work with the group"
                    ),
                )
            )

        spoiler_text = "\n".join(
            [
                character.concept,
                character.module_motivation,
                character.secret or "",
                *character.strengths,
            ]
        )
        spoiler_hits = [
            keyword
            for keyword in _extract_secret_keywords(module.core_secret)
            if keyword in spoiler_text
        ]
        if spoiler_hits:
            hard_errors.append(
                ErrorItem(
                    code="core_secret_spoiler",
                    message=(
                        "character already knows too much about the module core secret: "
                        f"{', '.join(sorted(spoiler_hits))}"
                    ),
                    field_path="secret",
                    severity="error",
                    suggestion=(
                        "replace direct knowledge with rumor, guilt, "
                        "suspicion, or incomplete fragments"
                    ),
                )
            )

        if not character.relationships:
            suggestions.append("建议补一条与其他玩家或关键 NPC 的初始关系，能显著改善开场黏合度。")

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
                "spoiler_hit_count": len(spoiler_hits),
                "relationship_count": len(character.relationships),
            },
        )
