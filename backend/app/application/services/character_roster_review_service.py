from backend.app.domain.enums.game import ValidationStatus
from backend.app.domain.schemas.character import CharacterSheetSchema
from backend.app.domain.schemas.common import ErrorItem, ValidationReport
from backend.app.domain.schemas.module import ModuleBlueprintSchema


class CharacterRosterReviewService:
    """在房间上下文里顺序审核角色之间是否冲突。"""

    def validate_against_roster(
        self,
        character: CharacterSheetSchema,
        existing_characters: list[CharacterSheetSchema],
        module: ModuleBlueprintSchema,
    ) -> ValidationReport:
        hard_errors: list[ErrorItem] = []
        warnings: list[ErrorItem] = []
        suggestions: list[str] = []

        if len(existing_characters) >= module.player_count_max:
            hard_errors.append(
                ErrorItem(
                    code="player_count_max_exceeded",
                    message=(
                        f"module allows at most {module.player_count_max} players, "
                        f"but {len(existing_characters)} are already approved"
                    ),
                    field_path="identity",
                    severity="error",
                    suggestion="reject this character or replace an already approved roster slot",
                )
            )

        for existing in existing_characters:
            if existing.name == character.name:
                hard_errors.append(
                    ErrorItem(
                        code="duplicate_character_name",
                        message=(
                            f"character name {character.name} duplicates an "
                            "approved roster member"
                        ),
                        field_path="name",
                        severity="error",
                        suggestion="rename the character to avoid roster confusion",
                    )
                )
            if existing.identity == character.identity:
                warnings.append(
                    ErrorItem(
                        code="duplicate_identity",
                        message=(
                            f"character identity {character.identity} is "
                            "already present in the roster"
                        ),
                        field_path="identity",
                        severity="warning",
                        suggestion=(
                            "differentiate the identity, hook, or narrative "
                            "seat from the existing role"
                        ),
                    )
                )
            if existing.secret and character.secret and existing.secret == character.secret:
                warnings.append(
                    ErrorItem(
                        code="duplicate_secret",
                        message="character secret duplicates an existing roster member's secret",
                        field_path="secret",
                        severity="warning",
                        suggestion=(
                            "rewrite the secret so each player owns a distinct "
                            "personal angle"
                        ),
                    )
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
                "approved_roster_size": len(existing_characters),
                "player_count_max": module.player_count_max,
            },
        )

    def review_queue(
        self,
        characters: list[CharacterSheetSchema],
        module: ModuleBlueprintSchema,
    ) -> list[ValidationReport]:
        reports: list[ValidationReport] = []
        approved_characters: list[CharacterSheetSchema] = []
        for character in characters:
            report = self.validate_against_roster(character, approved_characters, module)
            reports.append(report)
            if report.status == ValidationStatus.PASS:
                approved_characters.append(character)
        return reports
