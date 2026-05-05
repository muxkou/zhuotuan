import httpx

from backend.app.config import Settings
from backend.app.infra.llm.llm_client import LLMClient


async def test_llm_client_retries_timeout_once() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ReadTimeout("mock timeout", request=request)
        return httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": '{"ok": true}'}}]},
        )

    settings = Settings(
        llm_api_base_url="https://example.test",
        llm_api_key="test-key",
        llm_max_retries=1,
        llm_retry_backoff_seconds=0,
    )
    async with httpx.AsyncClient(
        base_url=settings.llm_api_base_url,
        transport=httpx.MockTransport(handler),
    ) as http_client:
        payload, raw_text = await LLMClient(
            settings=settings,
            http_client=http_client,
        ).generate_json_dict(
            system_prompt="system",
            user_prompt="user",
        )

    assert payload == {"ok": True}
    assert raw_text == '{"ok": true}'
    assert call_count == 2
