from collections.abc import Callable
from typing import Any


def _stringify_item(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("id", "name", "title", "role_name", "label", "text", "summary"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in item.values():
            if isinstance(value, str) and value.strip():
                return value.strip()
    return str(item)


def _stringify_list(items: list[Any]) -> list[str]:
    return [_stringify_item(item) for item in items]


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return _stringify_list(value)
    if isinstance(value, str):
        parts = [
            part.strip(" -\n\t")
            for part in value.replace("；", "\n").replace("。", "\n").splitlines()
            if part.strip(" -\n\t")
        ]
        return parts if parts else [value]
    return [_stringify_item(value)]


def normalize_world_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for key in (
        "tone",
        "public_rules",
        "hidden_rules",
        "factions",
        "common_locations",
        "taboos",
        "recommended_roles",
    ):
        if key in normalized:
            normalized[key] = _normalize_string_list(normalized[key])
    narration_style = normalized.get("narration_style")
    if isinstance(narration_style, dict):
        normalized["narration_style"] = {
            str(key): ", ".join(_normalize_string_list(value))
            if isinstance(value, (list, tuple, set, dict))
            else value
            for key, value in narration_style.items()
        }

    if "character_creation_profile" not in normalized:
        normalized["character_creation_profile"] = {
            "base_attributes": [
                {
                    "key": "physique",
                    "label": "体魄",
                    "description": "力量、耐力、负重、近身动作能力。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "体魄偏弱。"},
                        {"min_value": 1, "max_value": 2, "summary": "体魄正常。"},
                        {"min_value": 3, "max_value": 3, "summary": "体魄出众。"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "agility",
                    "label": "机敏",
                    "description": "反应、平衡、潜行与手上动作。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "动作偏慢。"},
                        {"min_value": 1, "max_value": 2, "summary": "机敏正常。"},
                        {"min_value": 3, "max_value": 3, "summary": "反应和动作非常灵活。"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "mind",
                    "label": "心智",
                    "description": "理解、推理、调查与知识整合。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "理解复杂信息比较吃力。"},
                        {"min_value": 1, "max_value": 2, "summary": "思维能力正常。"},
                        {"min_value": 3, "max_value": 3, "summary": "调查和推理能力非常强。"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "willpower",
                    "label": "意志",
                    "description": "抗压、忍耐、抵抗恐惧与诱惑。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "容易在压力下动摇。"},
                        {"min_value": 1, "max_value": 2, "summary": "意志力正常。"},
                        {"min_value": 3, "max_value": 3, "summary": "能在恐惧和压力中保持清醒。"},
                    ],
                    "is_core": True,
                },
                {
                    "key": "social",
                    "label": "社交",
                    "description": "说服、共情、读人和建立关系。",
                    "min_value": 0,
                    "max_value": 3,
                    "semantic_bands": [
                        {"min_value": 0, "max_value": 0, "summary": "不善表达或读人。"},
                        {"min_value": 1, "max_value": 2, "summary": "社交能力正常。"},
                        {"min_value": 3, "max_value": 3, "summary": "在人际判断和影响上明显强势。"},
                    ],
                    "is_core": True,
                },
            ],
            "world_specific_attributes": [],
            "total_attribute_budget_min": 0,
            "total_attribute_budget_max": 4,
            "identity_guidelines": _normalize_string_list(normalized.get("recommended_roles", [])),
            "forbidden_character_elements": [
                "明确可控的强超自然能力",
                "直接知道模组核心真相",
                "完全拒绝与队友合作的人设",
            ],
        }

    if "special_status_catalog" not in normalized:
        normalized["special_status_catalog"] = []
    return normalized


def normalize_module_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("module"), dict):
        normalized = dict(payload["module"])
    else:
        normalized = dict(payload)
    for key in ("required_npcs", "key_locations", "ai_do_not_change"):
        if key in normalized:
            normalized[key] = _normalize_string_list(normalized[key])

    freedom_level = normalized.get("ai_freedom_level")
    freedom_mapping = {
        "limited": "conservative",
        "low": "conservative",
        "medium": "standard",
        "normal": "standard",
        "default": "standard",
        "flexible": "high",
    }
    if isinstance(freedom_level, int):
        numeric_mapping = {
            1: "conservative",
            2: "standard",
            3: "high",
        }
        normalized["ai_freedom_level"] = numeric_mapping.get(freedom_level, "standard")
    elif isinstance(freedom_level, str):
        normalized_level = freedom_mapping.get(freedom_level, freedom_level)
        if normalized_level not in {"conservative", "standard", "high"}:
            lowered = normalized_level.lower()
            if "conservative" in lowered or "limited" in lowered or "保守" in normalized_level:
                normalized_level = "conservative"
            elif "high" in lowered or "自由" in normalized_level or "flexible" in lowered:
                normalized_level = "high"
            else:
                normalized_level = "standard"
        normalized["ai_freedom_level"] = normalized_level

    if isinstance(normalized.get("endings"), list):
        endings: dict[str, str] = {}
        for item in normalized["endings"]:
            if isinstance(item, dict):
                ending_key = item.get("type") or item.get("key") or item.get("name")
                ending_value = item.get("description") or item.get("text") or item.get("summary")
                if isinstance(ending_key, str) and isinstance(ending_value, str):
                    endings[ending_key] = ending_value
        normalized["endings"] = endings
    elif isinstance(normalized.get("endings"), dict):
        normalized["endings"] = {
            str(key): _stringify_item(value)
            for key, value in normalized["endings"].items()
        }

    raw_clues = normalized.get("key_clues")
    if isinstance(raw_clues, list):
        normalized_clues: list[dict[str, Any]] = []
        for clue in raw_clues:
            if isinstance(clue, dict):
                normalized_clues.append(
                    {
                        "clue_id": (
                            clue.get("clue_id")
                            or clue.get("id")
                            or clue.get("name")
                            or "unknown_clue"
                        ),
                        "target_secret_id": (
                            clue.get("target_secret_id")
                            or clue.get("secret_id")
                            or clue.get("secret")
                            or "core_secret"
                        ),
                        "location_id": (
                            clue.get("location_id")
                            or clue.get("location")
                            or clue.get("scene_id")
                        ),
                        "fallback_clue_ids": clue.get("fallback_clue_ids")
                        or clue.get("fallbacks")
                        or [],
                    }
                )
            else:
                normalized_clues.append(
                    {
                        "clue_id": _stringify_item(clue),
                        "target_secret_id": "core_secret",
                        "location_id": None,
                        "fallback_clue_ids": [],
                    }
                )
        normalized["key_clues"] = normalized_clues

    threat_clock_id = normalized.get("threat_clock_id")
    if not isinstance(threat_clock_id, str) or not threat_clock_id.strip():
        module_id = normalized.get("id") or "module"
        normalized["threat_clock_id"] = f"{module_id}_threat_clock"

    return normalized


def _coerce_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lstrip("-").isdigit():
            return int(stripped)
    return default


def _normalize_attribute_value(value: Any) -> int:
    numeric = _coerce_int(value, 0)
    if 0 <= numeric <= 3:
        return numeric
    if 0 <= numeric <= 10:
        return max(0, min(3, round(numeric / 3)))
    return max(0, min(3, numeric))


def _normalize_skill_value(value: Any) -> int:
    numeric = _coerce_int(value, 0)
    if 0 <= numeric <= 3:
        return numeric
    if 0 <= numeric <= 10:
        return max(0, min(3, round(numeric / 3)))
    return max(0, min(3, numeric))


def _normalize_numeric_mapping(
    value: Any,
    *,
    aliases: dict[str, str],
    defaults: dict[str, int],
    value_normalizer: Callable[[Any], int] | None = None,
) -> dict[str, int]:
    normalized = dict(defaults)
    if isinstance(value, dict):
        for key, raw_value in value.items():
            mapped_key = aliases.get(str(key), str(key))
            if mapped_key in normalized:
                coerced = _coerce_int(raw_value, normalized[mapped_key])
                normalized[mapped_key] = (
                    value_normalizer(coerced) if value_normalizer is not None else coerced
                )
    return normalized


def normalize_character_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("character"), dict):
        normalized = dict(payload["character"])
    else:
        normalized = dict(payload)

    list_fields = (
        "personality_tags",
        "strengths",
        "weaknesses",
        "fears",
        "inventory",
    )
    for key in list_fields:
        if key in normalized:
            normalized[key] = _normalize_string_list(normalized[key])

    if "module_motivation" not in normalized and "motivation" in normalized:
        normalized["module_motivation"] = _stringify_item(normalized["motivation"])

    attributes_aliases = {
        "physique": "physique",
        "体魄": "physique",
        "strength": "physique",
        "agility": "agility",
        "敏捷": "agility",
        "mind": "mind",
        "心智": "mind",
        "intelligence": "mind",
        "willpower": "willpower",
        "意志": "willpower",
        "social": "social",
        "社交": "social",
        "charisma": "social",
    }
    skill_aliases = {
        "investigation": "investigation",
        "调查": "investigation",
        "negotiation": "negotiation",
        "交涉": "negotiation",
        "stealth": "stealth",
        "潜行": "stealth",
        "combat": "combat",
        "战斗": "combat",
        "medicine": "medicine",
        "医疗": "medicine",
        "occult": "occult",
        "神秘学": "occult",
        "craft": "craft",
        "技艺": "craft",
        "survival": "survival",
        "生存": "survival",
    }
    raw_attributes = normalized.get("attributes")
    normalized["attributes"] = _normalize_numeric_mapping(
        raw_attributes,
        aliases=attributes_aliases,
        defaults={
            "physique": 0,
            "agility": 0,
            "mind": 0,
            "willpower": 0,
            "social": 0,
        },
        value_normalizer=_normalize_attribute_value,
    )
    extra_attributes: dict[str, int] = {}
    if isinstance(raw_attributes, dict):
        for key, raw_value in raw_attributes.items():
            string_key = str(key)
            if string_key not in attributes_aliases:
                extra_attributes[string_key] = _normalize_attribute_value(raw_value)
    if isinstance(normalized.get("extra_attributes"), dict):
        for key, raw_value in normalized["extra_attributes"].items():
            extra_attributes[str(key)] = _normalize_attribute_value(raw_value)
    normalized["extra_attributes"] = extra_attributes
    normalized["skills"] = _normalize_numeric_mapping(
        normalized.get("skills"),
        aliases=skill_aliases,
        defaults={
            "investigation": 0,
            "negotiation": 0,
            "stealth": 0,
            "combat": 0,
            "medicine": 0,
            "occult": 0,
            "craft": 0,
            "survival": 0,
        },
        value_normalizer=_normalize_skill_value,
    )

    relationships = normalized.get("relationships")
    if isinstance(relationships, list):
        normalized_relationships: list[dict[str, str]] = []
        for item in relationships:
            if isinstance(item, dict):
                relation: dict[str, str] = {}
                for key, value in item.items():
                    relation[str(key)] = _stringify_item(value)
                normalized_relationships.append(relation)
            else:
                normalized_relationships.append(
                    {
                        "target": "group",
                        "type": "默认关系",
                        "note": _stringify_item(item),
                    }
                )
        normalized["relationships"] = normalized_relationships
    elif isinstance(relationships, str):
        normalized["relationships"] = [
            {
                "target": "group",
                "type": "默认关系",
                "note": part,
            }
            for part in _normalize_string_list(relationships)
        ]
    else:
        normalized.setdefault("relationships", [])

    if "concept" not in normalized and "description" in normalized:
        normalized["concept"] = _stringify_item(normalized["description"])

    allowed_fields = {
        "id",
        "version",
        "created_at",
        "source",
        "name",
        "identity",
        "concept",
        "personality_tags",
        "module_motivation",
        "attributes",
        "extra_attributes",
        "skills",
        "strengths",
        "weaknesses",
        "fears",
        "secret",
        "relationships",
        "inventory",
    }
    return {
        key: value
        for key, value in normalized.items()
        if key in allowed_fields
    }
