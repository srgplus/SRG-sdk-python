"""Tests for the lazy workspace bootstrap on ``AsyncSRGClient``.

The pre-0.2 ``AsyncSRGClient`` never fetched workspaces, so any code that
tried to read ``client.workspace_id`` raised ``AttributeError``. The 0.2
async client exposes ``await client.get_workspace_id()`` which lazily fires
the same ``GET /api/v1/workspaces`` call the sync client used to do at
construction time.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from srg import AsyncSRGClient, SRGError

_BASE_URL = "https://gateway.srgplus.test"


class TestAsyncWorkspaceLazy:
    @respx.mock
    async def test_get_workspace_id_lazy_fetch(self) -> None:
        route = respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": "ws-async-1"}])
        )

        client = AsyncSRGClient(api_key="srgplus_x", base_url=_BASE_URL)
        # No request fired yet — async ctor must NOT eagerly bootstrap.
        assert route.call_count == 0
        assert client.workspace_id is None

        ws_id = await client.get_workspace_id()
        assert ws_id == "ws-async-1"
        assert route.call_count == 1
        # Cached:
        assert await client.get_workspace_id() == "ws-async-1"
        assert route.call_count == 1
        await client.aclose()

    @respx.mock
    async def test_get_workspace_id_uses_active_key(self) -> None:
        route = respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": "ws-async-2"}])
        )

        client = AsyncSRGClient(base_url=_BASE_URL)  # no default key
        async with client.use_api_key("srgplus_per_call"):
            ws_id = await client.get_workspace_id()

        assert ws_id == "ws-async-2"
        assert (
            route.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_per_call"
        )
        await client.aclose()

    @respx.mock
    async def test_get_workspace_id_raises_without_key(self) -> None:
        client = AsyncSRGClient(base_url=_BASE_URL)
        with pytest.raises(SRGError, match="No api_key bound"):
            await client.get_workspace_id()
        await client.aclose()

    @respx.mock
    async def test_get_workspace_id_raises_when_empty(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = AsyncSRGClient(api_key="srgplus_x", base_url=_BASE_URL)
        with pytest.raises(SRGError, match="No workspaces found"):
            await client.get_workspace_id()
        await client.aclose()

    @respx.mock
    async def test_async_client_no_attribute_error(self) -> None:
        """Reading ``workspace_id`` on a fresh async client returns ``None`` —
        not ``AttributeError`` like the 0.1 SDK did."""
        client = AsyncSRGClient(base_url=_BASE_URL)
        # The bug we're fixing: this used to crash.
        assert client.workspace_id is None
        await client.aclose()
