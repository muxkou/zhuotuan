from pydantic import ValidationError

from backend.app.domain.enums.game import ResolutionGrade
from backend.app.domain.schemas.ruleset import (
    AttributeScore,
    SkillBonus,
    validate_attributes,
    validate_skill_budget,
)
from backend.app.domain.value_objects.dice import (
    compute_check_total,
    grade_check_result,
    roll_2d6,
)


def test_attribute_score_out_of_field_range_raises() -> None:
    try:
        AttributeScore(physique=4, agility=0, mind=0, willpower=0, social=0)
    except ValidationError:
        pass
    else:
        raise AssertionError("expected ValidationError for out-of-range attribute field")

    try:
        AttributeScore(physique=-1, agility=0, mind=0, willpower=0, social=0)
    except ValidationError:
        pass
    else:
        raise AssertionError("expected ValidationError for negative attribute field")


def test_validate_attributes_detects_budget_overflow() -> None:
    errors = validate_attributes(
        AttributeScore(physique=1, agility=1, mind=1, willpower=1, social=1)
    )
    assert errors
    assert errors[0].code == "attribute_budget_out_of_range"


def test_validate_skill_budget_detects_budget_overflow() -> None:
    errors = validate_skill_budget(
        SkillBonus(
            investigation=2,
            negotiation=1,
            stealth=1,
            combat=1,
            medicine=1,
            occult=1,
        )
    )
    assert errors
    assert errors[0].code == "skill_budget_exceeded"


def test_roll_2d6_stays_in_expected_range() -> None:
    total, dice = roll_2d6(seed=42)
    assert len(dice) == 2
    assert all(1 <= die <= 6 for die in dice)
    assert 2 <= total <= 12


def test_compute_and_grade_check_result() -> None:
    total = compute_check_total(base_roll=7, attribute_mod=1, skill_mod=1)
    assert total == 9
    assert grade_check_result(total=13, difficulty=9) == ResolutionGrade.CRITICAL_SUCCESS
    assert grade_check_result(total=9, difficulty=9) == ResolutionGrade.SUCCESS
    assert grade_check_result(total=7, difficulty=9) == ResolutionGrade.MIXED
    assert grade_check_result(total=5, difficulty=9) == ResolutionGrade.FAILURE
    assert grade_check_result(total=3, difficulty=9) == ResolutionGrade.CRITICAL_FAILURE
