from random import Random

from backend.app.domain.enums.game import ResolutionGrade


def roll_2d6(seed: int | None = None) -> tuple[int, list[int]]:
    rng = Random(seed)
    dice = [rng.randint(1, 6), rng.randint(1, 6)]
    return sum(dice), dice


def compute_check_total(base_roll: int, attribute_mod: int, skill_mod: int) -> int:
    return base_roll + attribute_mod + skill_mod


def grade_check_result(total: int, difficulty: int) -> ResolutionGrade:
    if total >= difficulty + 4:
        return ResolutionGrade.CRITICAL_SUCCESS
    if total >= difficulty:
        return ResolutionGrade.SUCCESS
    if total >= difficulty - 2:
        return ResolutionGrade.MIXED
    if total <= difficulty - 5:
        return ResolutionGrade.CRITICAL_FAILURE
    return ResolutionGrade.FAILURE
