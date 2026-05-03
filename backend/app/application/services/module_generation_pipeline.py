from collections.abc import Callable

from backend.app.application.services.module_generation_service import ModuleGenerationService
from backend.app.application.validators.module_playability_validator import (
    ModulePlayabilityValidator,
)
from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.generation import (
    ModuleGenerationRunOutput,
    QuickStartInput,
)
from backend.app.domain.schemas.world import WorldSchema


class ModuleGenerationPipeline:
    """模组生成、校验、修补的一次完整编排。"""

    def __init__(
        self,
        module_service: ModuleGenerationService | None = None,
        validator: ModulePlayabilityValidator | None = None,
    ):
        self.module_service = module_service or ModuleGenerationService()
        self.validator = validator or ModulePlayabilityValidator()

    async def run(
        self,
        quick_start: QuickStartInput,
        world: WorldSchema,
        *,
        allow_repair: bool = True,
        progress_hook: Callable[[str], None] | None = None,
    ) -> ModuleGenerationRunOutput:
        if progress_hook:
            progress_hook("开始生成模组初稿")
        initial_output = await self.module_service.generate(quick_start, world)
        initial_report = self.validator.validate(initial_output.module, world)
        if progress_hook:
            progress_hook(
                f"模组初稿校验完成，初始状态: {initial_report.status}"
            )

        final_output = initial_output
        final_report = initial_report
        repair_attempted = False
        repaired = False
        repair_raw_text: str | None = None

        if allow_repair and initial_report.status in {ValidationStatus.WARN, ValidationStatus.FAIL}:
            repair_attempted = True
            if progress_hook:
                progress_hook("检测到 warn/fail，开始执行 repair pass")
            repaired_output = await self.module_service.repair(
                quick_start=quick_start,
                world=world,
                broken_module=initial_output.module,
                validation_summary=initial_report.model_dump(mode="json"),
            )
            repaired_report = self.validator.validate(repaired_output.module, world)
            final_output = repaired_output
            final_report = repaired_report
            repaired = True
            repair_raw_text = repaired_output.raw_text
            if progress_hook:
                progress_hook(
                    f"repair pass 完成，最终状态: {final_report.status}"
                )
        elif progress_hook:
            progress_hook("模组初稿直接通过，无需 repair")

        return ModuleGenerationRunOutput(
            module=final_output.module,
            initial_report=initial_report,
            final_report=final_report,
            repair_attempted=repair_attempted,
            repaired=repaired,
            initial_raw_text=initial_output.raw_text,
            repair_raw_text=repair_raw_text,
        )
