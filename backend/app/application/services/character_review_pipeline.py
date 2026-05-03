from collections.abc import Callable

from backend.app.application.services.character_generation_service import (
    CharacterGenerationService,
)
from backend.app.application.validators.character_module_validator import (
    CharacterModuleValidator,
)
from backend.app.application.validators.character_rules_validator import (
    CharacterRulesValidator,
)
from backend.app.application.validators.character_world_validator import (
    CharacterWorldValidator,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.generation import (
    CharacterGenerationRunOutput,
    CharacterQuestionnaire,
    CharacterReviewReport,
)
from backend.app.domain.schemas.module import ModuleBlueprintSchema
from backend.app.domain.schemas.ruleset import RuleSetSchema
from backend.app.domain.schemas.world import WorldSchema


def _status_rank(status: ValidationStatus) -> int:
    ranking = {
        ValidationStatus.FAIL: 0,
        ValidationStatus.WARN: 1,
        ValidationStatus.PASS: 2,
    }
    return ranking[status]


class CharacterReviewPipeline:
    """角色生成、审核、可选修补的一次完整编排。"""

    def __init__(
        self,
        generation_service: CharacterGenerationService | None = None,
        rules_validator: CharacterRulesValidator | None = None,
        world_validator: CharacterWorldValidator | None = None,
        module_validator: CharacterModuleValidator | None = None,
    ):
        self.generation_service = generation_service or CharacterGenerationService()
        self.rules_validator = rules_validator or CharacterRulesValidator()
        self.world_validator = world_validator or CharacterWorldValidator()
        self.module_validator = module_validator or CharacterModuleValidator()

    def review(
        self,
        character: CharacterSheetSchema,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
    ) -> CharacterReviewReport:
        rules_report = self.rules_validator.validate(character, ruleset)
        world_report = self.world_validator.validate(character, world)
        module_report = self.module_validator.validate(character, module)

        hard_errors = [
            *rules_report.hard_errors,
            *world_report.hard_errors,
            *module_report.hard_errors,
        ]
        warnings = [
            *rules_report.warnings,
            *world_report.warnings,
            *module_report.warnings,
        ]
        suggestion_pool = [
            *rules_report.suggestions,
            *world_report.suggestions,
            *module_report.suggestions,
        ]
        revision_suggestions = [
            *[item.suggestion for item in hard_errors if item.suggestion],
            *[item.suggestion for item in warnings if item.suggestion],
            *suggestion_pool,
        ]
        deduped_revision_suggestions = list(dict.fromkeys(revision_suggestions))

        if hard_errors:
            status = ValidationStatus.FAIL
            review_result = "needs_revision"
        elif warnings:
            status = ValidationStatus.WARN
            review_result = "warning"
        elif deduped_revision_suggestions:
            status = ValidationStatus.PASS
            review_result = "enhance"
        else:
            status = ValidationStatus.PASS
            review_result = "approved"

        return CharacterReviewReport(
            status=status,
            review_result=review_result,
            normalized_character=character,
            hard_errors=hard_errors,
            warnings=warnings,
            suggestions=suggestion_pool,
            blocking_reasons=[item.message for item in hard_errors],
            revision_suggestions=deduped_revision_suggestions,
            metrics={
                "hard_error_count": len(hard_errors),
                "warning_count": len(warnings),
                "rules_status": rules_report.status,
                "world_status": world_report.status,
                "module_status": module_report.status,
            },
        )

    async def run(
        self,
        questionnaire: CharacterQuestionnaire,
        world: WorldSchema,
        module: ModuleBlueprintSchema,
        ruleset: RuleSetSchema,
        *,
        allow_repair: bool = True,
        progress_hook: Callable[[str], None] | None = None,
    ) -> CharacterGenerationRunOutput:
        if progress_hook:
            progress_hook("开始生成角色初稿")
        initial_output = await self.generation_service.generate(
            questionnaire,
            world,
            module,
            ruleset,
        )
        initial_review_report = self.review(
            initial_output.character,
            world,
            module,
            ruleset,
        )
        if progress_hook:
            progress_hook(
                "角色初稿审核完成，"
                f"status={initial_review_report.status}, "
                f"review_result={initial_review_report.review_result}"
            )

        final_output = initial_output
        final_review_report = initial_review_report
        repair_attempted = False
        repaired = False
        repair_raw_text: str | None = None

        if allow_repair and initial_review_report.review_result in {"needs_revision", "warning"}:
            repair_attempted = True
            if progress_hook:
                progress_hook("检测到角色需要修订，开始执行 repair pass")
            repaired_output = await self.generation_service.repair(
                questionnaire=questionnaire,
                world=world,
                module=module,
                ruleset=ruleset,
                broken_character=initial_output.character,
                review_summary=initial_review_report.model_dump(mode="json"),
            )
            repaired_review_report = self.review(
                repaired_output.character,
                world,
                module,
                ruleset,
            )
            repair_raw_text = repaired_output.raw_text

            current_issue_count = len(initial_review_report.hard_errors) + len(
                initial_review_report.warnings
            )
            repaired_issue_count = len(repaired_review_report.hard_errors) + len(
                repaired_review_report.warnings
            )
            if (
                _status_rank(repaired_review_report.status)
                > _status_rank(initial_review_report.status)
                or (
                    repaired_review_report.status == initial_review_report.status
                    and repaired_issue_count < current_issue_count
                )
            ):
                final_output = repaired_output
                final_review_report = repaired_review_report
                repaired = True
            if progress_hook:
                progress_hook(
                    "角色 repair pass 完成，"
                    f"final_status={final_review_report.status}, "
                    f"final_review_result={final_review_report.review_result}, "
                    f"accepted={repaired}"
                )
        elif progress_hook:
            progress_hook("角色初稿已可接受，无需 repair")

        return CharacterGenerationRunOutput(
            character=final_output.character,
            initial_review_report=initial_review_report,
            final_review_report=final_review_report,
            repair_attempted=repair_attempted,
            repaired=repaired,
            initial_raw_text=initial_output.raw_text,
            repair_raw_text=repair_raw_text,
        )
