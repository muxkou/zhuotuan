import json
import re
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from backend.app.config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


class LLMConfigurationError(RuntimeError):
    """LLM 配置不完整时抛出的错误。"""


class LLMResponseError(RuntimeError):
    """LLM 返回内容无法使用时抛出的错误。"""


@dataclass(slots=True)
class LLMGenerationResult:
    """统一的模型调用结果。"""

    content: str
    raw_response: dict[str, Any]


class LLMClient:
    """统一的 OpenAI-compatible 聊天补全客户端。"""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.settings = settings or get_settings()
        self._http_client = http_client

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> LLMGenerationResult:
        if not self.settings.llm_api_base_url or not self.settings.llm_api_key:
            raise LLMConfigurationError("LLM API base URL or API key is missing.")

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.settings.llm_temperature if temperature is None else temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        close_client = False
        client = self._http_client
        if client is None:
            client = httpx.AsyncClient(
                base_url=self.settings.llm_api_base_url.rstrip("/"),
                timeout=self.settings.llm_timeout_seconds,
            )
            close_client = True

        try:
            response = await client.post(
                self.settings.llm_chat_completions_path,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            raw = response.json()
            content = raw["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise LLMResponseError("LLM returned empty content.")
            return LLMGenerationResult(content=content, raw_response=raw)
        finally:
            if close_client:
                await client.aclose()

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        temperature: float | None = None,
    ) -> tuple[T, str]:
        result = await self.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        try:
            parsed = json.loads(result.content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError("LLM did not return valid JSON.") from exc
        return response_model.model_validate(parsed), result.content

    async def generate_json_dict(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> tuple[dict[str, Any], str]:
        result = await self.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        try:
            parsed = self._parse_json_object(result.content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError("LLM did not return valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise LLMResponseError("LLM JSON root must be an object.")
        return parsed, result.content

    @staticmethod
    def _parse_json_object(content: str) -> Any:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if fenced_match:
            candidate = fenced_match.group(1)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                content = candidate

        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start : end + 1]

        sanitized = "".join(
            char
            for char in content
            if char in ("\n", "\r", "\t") or ord(char) >= 32
        )
        return json.loads(sanitized)
