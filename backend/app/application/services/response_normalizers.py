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
    return normalized


def normalize_module_payload(payload: dict[str, Any]) -> dict[str, Any]:
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
    if isinstance(freedom_level, str):
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

    return normalized
