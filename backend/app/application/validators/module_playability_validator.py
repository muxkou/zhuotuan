from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.common import ErrorItem
from backend.app.domain.schemas.generation import ModulePlayabilityReport
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.world import WorldSchema


class ModulePlayabilityValidator:
    """检查模组是否满足阶段一可运行要求。"""

    def validate(
        self,
        module: ModuleBlueprintSchema,
        world: WorldSchema,
    ) -> ModulePlayabilityReport:
        missing_core_fields: list[str] = []
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        for field_name in (
            "core_secret",
            "opening_hook",
            "major_conflict",
            "required_npcs",
            "key_locations",
            "key_clues",
            "endings",
            "ai_do_not_change",
        ):
            value = getattr(module, field_name)
            if value is None or value == "" or value == [] or value == {}:
                missing_core_fields.append(field_name)

        if missing_core_fields:
            hard_errors.append(
                ErrorItem(
                    code="missing_core_fields",
                    message=f"module is missing required fields: {missing_core_fields}",
                    field_path="module",
                    severity="error",
                    suggestion="fill all required module blueprint fields before running the game",
                )
            )

        clue_path_count = len(module.key_clues)
        if clue_path_count < 3:
            warnings.append(
                ErrorItem(
                    code="insufficient_core_clues",
                    message="fewer than 3 key clues point to the core secret",
                    field_path="key_clues",
                    severity="warning",
                    suggestion="add more independent clue paths to reduce dead ends",
                )
            )
            suggestions.append("至少补充到 3 条关键线索指向核心秘密。")

        fallback_count = sum(1 for clue in module.key_clues if clue.fallback_clue_ids)
        if fallback_count == 0:
            warnings.append(
                ErrorItem(
                    code="missing_fallback_clues",
                    message="no fallback clue path is configured",
                    field_path="key_clues",
                    severity="warning",
                    suggestion="configure at least one fallback clue to avoid hard locks",
                )
            )
            suggestions.append("至少给一条关键线索配置替代获取路径。")

        required_endings = {"good", "partial", "bad"}
        if not required_endings.issubset(module.endings):
            hard_errors.append(
                ErrorItem(
                    code="missing_required_endings",
                    message="good/partial/bad endings must all be present",
                    field_path="endings",
                    severity="error",
                    suggestion="add the three baseline ending outcomes",
                )
            )

        if len(world.public_rules) == 0:
            warnings.append(
                ErrorItem(
                    code="world_public_rules_empty",
                    message="world has no public rules for players",
                    field_path="world.public_rules",
                    severity="warning",
                    suggestion="provide visible world rules to support onboarding",
                )
            )

        if hard_errors:
            status = ValidationStatus.FAIL
        elif warnings:
            status = ValidationStatus.WARN
        else:
            status = ValidationStatus.PASS

        return ModulePlayabilityReport(
            status=status,
            hard_errors=hard_errors,
            warnings=warnings,
            suggestions=suggestions,
            metrics={
                "required_npc_count": len(module.required_npcs),
                "key_location_count": len(module.key_locations),
                "ending_count": len(module.endings),
                "fallback_clue_count": fallback_count,
            },
            missing_core_fields=missing_core_fields,
            uncovered_secret_ids=[],
            clue_path_count=clue_path_count,
        )
