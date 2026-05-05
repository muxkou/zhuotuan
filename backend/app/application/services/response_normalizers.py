from collections.abc import Callable
from typing import Any

from backend.app.domain.schemas.world import (
    default_character_creation_profile,
    default_special_status_catalog,
)


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


def _attribute_key_from_label(label: str, index: int) -> str:
    mapping = {
        "体魄": "physique",
        "体质": "physique",
        "力量": "physique",
        "机敏": "agility",
        "灵巧": "agility",
        "敏捷": "agility",
        "心智": "mind",
        "智力": "mind",
        "洞察": "mind",
        "意志": "willpower",
        "精神": "willpower",
        "社交": "social",
        "魅力": "social",
    }
    stripped = label.strip()
    return mapping.get(stripped, f"world_attr_{index}")


def _default_character_creation_profile_payload() -> dict[str, Any]:
    return default_character_creation_profile().model_dump(mode="json")


def _default_special_status_catalog_payload() -> list[dict[str, Any]]:
    return [
        item.model_dump(mode="json")
        for item in default_special_status_catalog()
    ]


def _attribute_definition_from_label(label: str, index: int, *, is_core: bool) -> dict[str, Any]:
    key = _attribute_key_from_label(label, index)
    return {
        "key": key,
        "label": label.strip() or f"世界属性{index + 1}",
        "description": f"{label} 是当前世界车卡时可使用的属性。",
        "min_value": 0,
        "max_value": 3,
        "semantic_bands": [
            {"min_value": 0, "max_value": 0, "summary": f"{label}较弱。"},
            {"min_value": 1, "max_value": 2, "summary": f"{label}正常。"},
            {"min_value": 3, "max_value": 3, "summary": f"{label}突出。"},
        ],
        "is_core": is_core,
    }


def _skill_key_from_label(label: str, index: int) -> str:
    mapping = {
        "调查": "investigation",
        "侦查": "investigation",
        "交涉": "negotiation",
        "说服": "negotiation",
        "潜行": "stealth",
        "隐匿": "stealth",
        "战斗": "combat",
        "格斗": "combat",
        "医治": "medicine",
        "医疗": "medicine",
        "民俗": "occult",
        "神秘学": "occult",
        "技艺": "craft",
        "手工": "craft",
        "生存": "survival",
    }
    stripped = label.strip()
    return mapping.get(stripped, f"world_skill_{index + 1}")


def _normalize_skill_definition(item: Any, index: int) -> dict[str, str]:
    if isinstance(item, dict):
        label = _stringify_item(
            item.get("label")
            or item.get("name")
            or item.get("名称")
            or item.get("key")
            or f"世界技能{index + 1}"
        )
        key = str(item.get("key") or _skill_key_from_label(label, index)).strip()
        return {
            "key": key or f"world_skill_{index + 1}",
            "label": label,
            "description": _stringify_item(
                item.get("description")
                or item.get("描述")
                or f"{label} 是当前世界车卡时可选择的技能。"
            ),
        }
    label = _stringify_item(item)
    return {
        "key": _skill_key_from_label(label, index),
        "label": label,
        "description": f"{label} 是当前世界车卡时可选择的技能。",
    }


def normalize_character_creation_profile_payload(
    value: Any,
    normalized: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_profile = _default_character_creation_profile_payload()
    normalized = normalized or {}
    if not isinstance(value, dict):
        return default_profile

    if isinstance(value.get("base_attributes"), list):
        profile = dict(value)
        profile.setdefault("world_specific_attributes", [])
        profile.setdefault("total_attribute_budget_min", 0)
        profile.setdefault("total_attribute_budget_max", 4)
        profile.setdefault("skills", default_profile["skills"])
        profile.setdefault("total_skill_points", default_profile["total_skill_points"])
        profile.setdefault(
            "skill_level_descriptions",
            default_profile["skill_level_descriptions"],
        )
        profile.setdefault(
            "identity_guidelines",
            _normalize_string_list(normalized.get("recommended_roles", [])),
        )
        profile.setdefault(
            "forbidden_character_elements",
            default_profile["forbidden_character_elements"],
        )
        profile["skills"] = [
            _normalize_skill_definition(item, index)
            for index, item in enumerate(profile.get("skills") or default_profile["skills"])
        ]
        return profile

    raw_attributes = (
        value.get("属性")
        or value.get("attributes")
        or value.get("base_attributes")
        or []
    )
    attribute_labels = _normalize_string_list(raw_attributes)
    if attribute_labels:
        base_attributes = [
            _attribute_definition_from_label(label, index, is_core=True)
            for index, label in enumerate(attribute_labels)
        ]
    else:
        base_attributes = default_profile["base_attributes"]

    special_labels = _normalize_string_list(
        value.get("特色能力槽") or value.get("特殊属性") or []
    )
    world_specific_attributes = [
        _attribute_definition_from_label(label, index, is_core=False)
        for index, label in enumerate(special_labels)
    ]

    identity_guidelines = _normalize_string_list(normalized.get("recommended_roles", []))
    equipment_guidelines = _normalize_string_list(value.get("初始装备") or [])
    if equipment_guidelines:
        identity_guidelines.extend(
            f"建议初始装备：{item}"
            for item in equipment_guidelines
        )
    raw_skills = (
        value.get("skills")
        or value.get("技能")
        or value.get("skill_list")
        or value.get("车卡技能")
        or default_profile["skills"]
    )
    skill_items = raw_skills if isinstance(raw_skills, list) else _normalize_string_list(raw_skills)
    skill_points = _coerce_int(
        value.get("total_skill_points")
        or value.get("skill_points_total")
        or value.get("总技能点")
        or value.get("技能点总量"),
        default_profile["total_skill_points"],
    )

    return {
        "base_attributes": base_attributes,
        "world_specific_attributes": world_specific_attributes,
        "total_attribute_budget_min": 0,
        "total_attribute_budget_max": 4,
        "skills": [
            _normalize_skill_definition(item, index)
            for index, item in enumerate(skill_items)
        ],
        "total_skill_points": max(0, skill_points),
        "skill_level_descriptions": default_profile["skill_level_descriptions"],
        "identity_guidelines": identity_guidelines,
        "forbidden_character_elements": default_profile["forbidden_character_elements"],
    }


def _normalize_special_status_catalog(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return _default_special_status_catalog_payload()
    if isinstance(value, list):
        statuses: list[dict[str, Any]] = []
        for index, item in enumerate(value):
            if isinstance(item, dict):
                label = (
                    item.get("label")
                    or item.get("name")
                    or item.get("名称")
                    or item.get("key")
                    or f"特殊状态{index + 1}"
                )
                statuses.append(
                    {
                        "key": str(item.get("key") or f"status_{index + 1}"),
                        "label": _stringify_item(label),
                        "description": _stringify_item(
                            item.get("description") or item.get("描述") or item
                        ),
                        "trigger_sources": _normalize_string_list(
                            item.get("trigger_sources") or item.get("触发来源") or ["剧情触发"]
                        ),
                        "behavioral_constraints": _normalize_string_list(
                            item.get("behavioral_constraints")
                            or item.get("行为约束")
                            or item.get("效果")
                            or item
                        ),
                        "recovery_hints": _normalize_string_list(
                            item.get("recovery_hints") or item.get("恢复提示") or []
                        ),
                    }
                )
            else:
                label = _stringify_item(item)
                statuses.append(
                    {
                        "key": f"status_{index + 1}",
                        "label": label,
                        "description": label,
                        "trigger_sources": ["剧情触发"],
                        "behavioral_constraints": [label],
                        "recovery_hints": [],
                    }
                )
        return statuses
    if isinstance(value, dict):
        statuses = []
        for index, (label, description) in enumerate(value.items()):
            statuses.append(
                {
                    "key": f"status_{index + 1}",
                    "label": str(label),
                    "description": _stringify_item(description),
                    "trigger_sources": ["剧情触发"],
                    "behavioral_constraints": _normalize_string_list(description),
                    "recovery_hints": [],
                }
            )
        return statuses
    return _default_special_status_catalog_payload()


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

    normalized["character_creation_profile"] = normalize_character_creation_profile_payload(
        normalized.get("character_creation_profile"),
        normalized,
    )
    normalized["special_status_catalog"] = _normalize_special_status_catalog(
        normalized.get("special_status_catalog")
    )
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
    if isinstance(freedom_level, float):
        if freedom_level < 0.34:
            normalized["ai_freedom_level"] = "conservative"
        elif freedom_level <= 0.66:
            normalized["ai_freedom_level"] = "standard"
        else:
            normalized["ai_freedom_level"] = "high"
    elif isinstance(freedom_level, int):
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
    if 0 <= numeric <= 2:
        return numeric
    if 0 <= numeric <= 10:
        return max(0, min(2, round(numeric / 5)))
    return max(0, min(2, numeric))


def _normalize_numeric_mapping(
    value: Any,
    *,
    aliases: dict[str, str],
    defaults: dict[str, int],
    value_normalizer: Callable[[Any], int] | None = None,
    allow_new_keys: bool = False,
) -> dict[str, int]:
    normalized = dict(defaults)
    if isinstance(value, dict):
        for key, raw_value in value.items():
            mapped_key = aliases.get(str(key), str(key))
            if mapped_key in normalized or allow_new_keys:
                coerced = _coerce_int(raw_value, normalized.get(mapped_key, 0))
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
        defaults={},
        value_normalizer=_normalize_skill_value,
        allow_new_keys=True,
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
