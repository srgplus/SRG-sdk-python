"""Tests for AsyncSRGClient bootstrap behaviour."""

from __future__ import annotations

import httpx
import pytest
import respx

from srg import AsyncSRGClient, SRGError

_BASE_URL = "https://gateway.srgplus.test"


class TestAsyncBootstrap:
    @respx.mock
    async def test_bootstrap_via_async_with(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": "ws-async-1"}])
        )

        async with AsyncSRGClient(api_keys=["srgplus_x"], base_url=_BASE_URL) as client:
            assert "ws-async-1" in client._registry

    @respx.mock
    async def test_bootstrap_via_explicit_call(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": "ws-async-2"}])
        )

        client = AsyncSRGClient(api_keys=["srgplus_x"], base_url=_BASE_URL)
        assert not client._registry  # not bootstrapped yet
        await client.bootstrap()
        assert "ws-async-2" in client._registry
        await client.aclose()

    @respx.mock
    async def test_bootstrap_is_idempotent(self) -> None:
        route = respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": "ws-async-3"}])
        )

        async with AsyncSRGClient(api_keys=["srgplus_x"], base_url=_BASE_URL) as client:
            await client.bootstrap()  # second call — must not re-fetch
            assert route.call_count == 1

    @respx.mock
    async def test_bootstrap_raises_on_empty_workspaces(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[])
        )
        with pytest.raises(SRGError, match="No workspaces found"):
            async with AsyncSRGClient(api_keys=["srgplus_x"], base_url=_BASE_URL):
                pass

    @respx.mock
    async def test_registry_empty_before_bootstrap(self) -> None:
        client = AsyncSRGClient(api_keys=["srgplus_x"], base_url=_BASE_URL)
        assert not client._registry
        await client.aclose()
