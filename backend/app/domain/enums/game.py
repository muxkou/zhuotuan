from enum import StrEnum


class AiFreedomLevel(StrEnum):
    CONSERVATIVE = "conservative"
    STANDARD = "standard"
    HIGH = "high"


class ValidationStatus(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class ArtifactSource(StrEnum):
    HUMAN = "human"
    LLM = "llm"
    SYSTEM = "system"
    IMPORTED = "imported"


class ActorType(StrEnum):
    PLAYER = "player"
    KP = "kp"
    SYSTEM = "system"


class ResolutionGrade(StrEnum):
    CRITICAL_SUCCESS = "critical_success"
    SUCCESS = "success"
    MIXED = "mixed"
    FAILURE = "failure"
    CRITICAL_FAILURE = "critical_failure"
