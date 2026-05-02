"""Tests for the per-request ``api_key`` API (SRGDEV-14).

Verifies that ``with_api_key`` and ``use_api_key`` cause each outbound HTTP
request to carry the bound key in its ``Authorization`` header — without
mutating the underlying ``httpx.Client`` headers (so a single connection pool
can safely serve many workspaces concurrently).
"""

from __future__ import annotations

import httpx
import pytest
import respx

from srg import AsyncSRGClient, SRGClient, SRGError

_BASE_URL = "https://gateway.srgplus.test"
_WORKSPACE_PAYLOAD = [{"id": "ws-default"}]


class TestSyncWithApiKey:
    @respx.mock
    def test_with_api_key_sends_bound_key(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = SRGClient(base_url=_BASE_URL)  # no default key

        scoped = client.with_api_key("srgplus_a")
        scoped.workspaces.list_actions("ws-default")

        last_request = respx.calls.last.request
        assert last_request.headers["Authorization"] == "Bearer srgplus_a"
        client.close()

    @respx.mock
    def test_two_scoped_clients_send_different_keys(self) -> None:
        # Two scoped views over ONE underlying client — each request must
        # carry its own key.
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = SRGClient(base_url=_BASE_URL)
        a = client.with_api_key("srgplus_a")
        b = client.with_api_key("srgplus_b")

        a.workspaces.list_actions("ws-default")
        first_auth = respx.calls.last.request.headers["Authorization"]

        b.workspaces.list_actions("ws-default")
        second_auth = respx.calls.last.request.headers["Authorization"]

        assert first_auth == "Bearer srgplus_a"
        assert second_auth == "Bearer srgplus_b"
        assert first_auth != second_auth
        client.close()

    @respx.mock
    def test_use_api_key_context_manager(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = SRGClient(base_url=_BASE_URL)
        with client.use_api_key("srgplus_ctx"):
            client.workspaces.list_actions("ws-default")

        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_ctx"
        )
        client.close()

    @respx.mock
    def test_request_without_key_raises(self) -> None:
        client = SRGClient(base_url=_BASE_URL)
        with pytest.raises(SRGError, match="No api_key bound"):
            client.workspaces.list_actions("ws-default")
        client.close()

    @respx.mock
    def test_default_key_used_when_no_binding(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=_WORKSPACE_PAYLOAD)
        )
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = SRGClient(api_key="srgplus_default", base_url=_BASE_URL)
        # Eager bootstrap fired with the default key:
        bootstrap_call = respx.calls[0]
        assert (
            bootstrap_call.request.headers["Authorization"]
            == "Bearer srgplus_default"
        )

        client.workspaces.list_actions("ws-default")
        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_default"
        )
        client.close()

    @respx.mock
    def test_scoped_overrides_default_key(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=_WORKSPACE_PAYLOAD)
        )
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = SRGClient(api_key="srgplus_default", base_url=_BASE_URL)
        scoped = client.with_api_key("srgplus_override")
        scoped.workspaces.list_actions("ws-default")

        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_override"
        )
        client.close()


class TestAsyncWithApiKey:
    @respx.mock
    async def test_async_with_api_key_sends_bound_key(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = AsyncSRGClient(base_url=_BASE_URL)
        scoped = client.with_api_key("srgplus_async_a")
        await scoped.workspaces.list_actions("ws-default")

        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_async_a"
        )
        await client.aclose()

    @respx.mock
    async def test_async_use_api_key_context_manager(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = AsyncSRGClient(base_url=_BASE_URL)
        async with client.use_api_key("srgplus_async_ctx"):
            await client.workspaces.list_actions("ws-default")

        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_async_ctx"
        )
        await client.aclose()

    @respx.mock
    async def test_async_request_without_key_raises(self) -> None:
        client = AsyncSRGClient(base_url=_BASE_URL)
        with pytest.raises(SRGError, match="No api_key bound"):
            await client.workspaces.list_actions("ws-default")
        await client.aclose()

    @respx.mock
    async def test_async_with_api_key_supports_async_with(self) -> None:
        # Regression test (SRGDEV-22): ``async with client.with_api_key(key)``
        # must enter/exit cleanly and the bound key must be used inside.
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = AsyncSRGClient(base_url=_BASE_URL)
        async with client.with_api_key("srgplus_async_with") as scoped:
            await scoped.workspaces.list_actions("ws-default")

        assert (
            respx.calls.last.request.headers["Authorization"]
            == "Bearer srgplus_async_with"
        )
        # ``__aexit__`` closed the parent — opening another scoped view on
        # the same client after the block must not be expected to work; the
        # test purpose is just to assert the protocol is supported.

    @respx.mock
    async def test_two_async_scoped_clients_send_different_keys(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = AsyncSRGClient(base_url=_BASE_URL)
        a = client.with_api_key("srgplus_a")
        b = client.with_api_key("srgplus_b")

        await a.workspaces.list_actions("ws-default")
        first_auth = respx.calls.last.request.headers["Authorization"]
        await b.workspaces.list_actions("ws-default")
        second_auth = respx.calls.last.request.headers["Authorization"]

        assert first_auth == "Bearer srgplus_a"
        assert second_auth == "Bearer srgplus_b"
        await client.aclose()


class TestSharedConnectionPool:
    """Both scoped clients must share the same underlying httpx client."""

    @respx.mock
    def test_sync_scoped_clients_share_pool(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces/ws-default/actions").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = SRGClient(base_url=_BASE_URL)
        a = client.with_api_key("srgplus_a")
        b = client.with_api_key("srgplus_b")
        # Both wrappers must drive the same httpx.Client instance.
        # ``a._parent`` and ``b._parent`` are the SRGClient; the http object
        # is what matters.
        assert a._parent._http is b._parent._http  # type: ignore[attr-defined]
        client.close()
