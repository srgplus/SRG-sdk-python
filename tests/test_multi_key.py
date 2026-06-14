"""Tests for the multi-key SRGClient / AsyncSRGClient API."""

from __future__ import annotations

import httpx
import pytest
import respx

from srg import AsyncSRGClient, SRGClient, SRGError

_BASE_URL = "https://gateway.srgplus.test"
_WS_1 = "ws-uuid-1"
_WS_2 = "ws-uuid-2"
_KEY_1 = "srgplus_key_1"
_KEY_2 = "srgplus_key_2"

# A user-level key (srgplus_u_) resolves to MANY workspaces with one key.
_USER_KEY = "srgplus_u_userlevelkey"
_USER_WS = ["ws-user-a", "ws-user-b", "ws-user-c"]


def _mock_workspaces(keys_to_ws: dict[str, str]) -> None:
    """Register /api/v1/workspaces mock that returns correct ws per key."""

    def _side_effect(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("Authorization", "")
        for key, ws_id in keys_to_ws.items():
            if auth == f"Bearer {key}":
                return httpx.Response(200, json=[{"id": ws_id}])
        return httpx.Response(401, json={"detail": "Unauthorized"})

    respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(side_effect=_side_effect)


class TestSyncMultiKey:
    @respx.mock
    def test_single_key_bootstrap(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1})
        client = SRGClient(api_keys=[_KEY_1], base_url=_BASE_URL)
        assert _WS_1 in client._registry
        client.close()

    @respx.mock
    def test_multi_key_builds_registry(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1, _KEY_2: _WS_2})
        client = SRGClient(api_keys=[_KEY_1, _KEY_2], base_url=_BASE_URL)
        assert set(client._registry.keys()) == {_WS_1, _WS_2}
        client.close()

    @respx.mock
    def test_multi_key_routes_correct_auth(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1, _KEY_2: _WS_2})
        respx.get(f"{_BASE_URL}/api/v1/workspaces/{_WS_1}/hub-profiles").mock(
            return_value=httpx.Response(200, json=[])
        )
        respx.get(f"{_BASE_URL}/api/v1/workspaces/{_WS_2}/hub-profiles").mock(
            return_value=httpx.Response(200, json=[])
        )

        client = SRGClient(api_keys=[_KEY_1, _KEY_2], base_url=_BASE_URL)

        client.hub_profiles.list(workspace_id=_WS_1)
        assert respx.calls.last.request.headers["Authorization"] == f"Bearer {_KEY_1}"

        client.hub_profiles.list(workspace_id=_WS_2)
        assert respx.calls.last.request.headers["Authorization"] == f"Bearer {_KEY_2}"
        client.close()

    @respx.mock
    def test_unknown_workspace_raises(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1})
        client = SRGClient(api_keys=[_KEY_1], base_url=_BASE_URL)
        with pytest.raises(SRGError, match="No API key registered"):
            client.hub_profiles.list(workspace_id="nonexistent-ws")
        client.close()

    @respx.mock
    def test_no_key_raises(self) -> None:
        import os

        os.environ.pop("SRG_API_KEYS", None)
        with pytest.raises(SRGError, match="api_keys must be provided"):
            SRGClient(base_url=_BASE_URL)

    @respx.mock
    def test_empty_workspace_list_raises(self) -> None:
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[])
        )
        with pytest.raises(SRGError, match="No workspaces found"):
            SRGClient(api_keys=[_KEY_1], base_url=_BASE_URL)

    @respx.mock
    def test_invalid_key_skipped_if_another_valid(self) -> None:
        """Keys that return no workspace are silently skipped."""
        _mock_workspaces({_KEY_1: _WS_1})  # _KEY_2 returns 401, no workspace
        client = SRGClient(api_keys=[_KEY_1, _KEY_2], base_url=_BASE_URL)
        assert set(client._registry.keys()) == {_WS_1}
        client.close()

    @respx.mock
    def test_user_level_key_registers_all_workspaces(self) -> None:
        """ONE user-level key returning many workspaces registers them ALL.

        Regression: the client used to keep only raw[0], so a srgplus_u_ key
        with N workspaces exposed just the first one (the connector showed a
        single workspace and could not reach any of the others).
        """
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": w} for w in _USER_WS])
        )
        client = SRGClient(api_keys=[_USER_KEY], base_url=_BASE_URL)
        assert set(client._registry.keys()) == set(_USER_WS)
        # all workspaces share the single user-key HTTP client
        assert len(set(client._registry.values())) == 1
        client.close()

    @respx.mock
    def test_user_level_key_routes_to_non_first_workspace(self) -> None:
        """Targeting a workspace that is NOT raw[0] must work (pre-fix it
        raised 'No API key registered for workspace ...')."""
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": w} for w in _USER_WS])
        )
        respx.get(
            f"{_BASE_URL}/api/v1/workspaces/{_USER_WS[2]}/hub-profiles"
        ).mock(return_value=httpx.Response(200, json=[]))
        client = SRGClient(api_keys=[_USER_KEY], base_url=_BASE_URL)
        client.hub_profiles.list(workspace_id=_USER_WS[2])
        assert (
            respx.calls.last.request.headers["Authorization"]
            == f"Bearer {_USER_KEY}"
        )
        client.close()


class TestAsyncMultiKey:
    @respx.mock
    async def test_single_key_bootstrap(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1})
        async with AsyncSRGClient(api_keys=[_KEY_1], base_url=_BASE_URL) as client:
            assert _WS_1 in client._registry

    @respx.mock
    async def test_multi_key_builds_registry(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1, _KEY_2: _WS_2})
        async with AsyncSRGClient(
            api_keys=[_KEY_1, _KEY_2], base_url=_BASE_URL
        ) as client:
            assert set(client._registry.keys()) == {_WS_1, _WS_2}

    @respx.mock
    async def test_multi_key_routes_correct_auth(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1, _KEY_2: _WS_2})
        respx.get(f"{_BASE_URL}/api/v1/workspaces/{_WS_1}/hub-profiles").mock(
            return_value=httpx.Response(200, json=[])
        )
        respx.get(f"{_BASE_URL}/api/v1/workspaces/{_WS_2}/hub-profiles").mock(
            return_value=httpx.Response(200, json=[])
        )

        async with AsyncSRGClient(
            api_keys=[_KEY_1, _KEY_2], base_url=_BASE_URL
        ) as client:
            await client.hub_profiles.list(workspace_id=_WS_1)
            assert (
                respx.calls.last.request.headers["Authorization"] == f"Bearer {_KEY_1}"
            )

            await client.hub_profiles.list(workspace_id=_WS_2)
            assert (
                respx.calls.last.request.headers["Authorization"] == f"Bearer {_KEY_2}"
            )

    @respx.mock
    async def test_user_level_key_registers_all_workspaces(self) -> None:
        """ONE user-level key returning many workspaces registers them ALL."""
        respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": w} for w in _USER_WS])
        )
        async with AsyncSRGClient(
            api_keys=[_USER_KEY], base_url=_BASE_URL
        ) as client:
            assert set(client._registry.keys()) == set(_USER_WS)
            assert len(set(client._registry.values())) == 1

    @respx.mock
    async def test_manual_bootstrap(self) -> None:
        _mock_workspaces({_KEY_1: _WS_1})
        client = AsyncSRGClient(api_keys=[_KEY_1], base_url=_BASE_URL)
        assert not client._registry  # not bootstrapped yet
        await client.bootstrap()
        assert _WS_1 in client._registry
        await client.aclose()

    @respx.mock
    async def test_bootstrap_is_idempotent(self) -> None:
        route = respx.get(f"{_BASE_URL}/api/v1/workspaces").mock(
            return_value=httpx.Response(200, json=[{"id": _WS_1}])
        )
        async with AsyncSRGClient(api_keys=[_KEY_1], base_url=_BASE_URL) as client:
            await client.bootstrap()  # second call — must not re-fetch
            assert route.call_count == 1
