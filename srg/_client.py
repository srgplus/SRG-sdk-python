import os
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from functools import cached_property

from srg._http import AsyncHTTPClient, SyncHTTPClient, _active_api_key
from srg.exceptions import SRGError
from srg.resources.assets import AssetsResource, AsyncAssetsResource
from srg.resources.channels import AsyncChannelsResource, ChannelsResource
from srg.resources.contents import AsyncContentsResource, ContentsResource
from srg.resources.hub_profiles import AsyncHubProfilesResource, HubProfilesResource
from srg.resources.invitations import AsyncInvitationsResource, InvitationsResource
from srg.resources.permission_groups import (
    AsyncPermissionGroupsResource,
    PermissionGroupsResource,
)
from srg.resources.permissions import AsyncPermissionsResource, PermissionsResource
from srg.resources.users import AsyncUsersResource, UsersResource
from srg.resources.workspaces import AsyncWorkspacesResource, WorkspacesResource

_DEFAULT_BASE_URL = "https://gateway.srgplus.com"


def _resolve_api_key(value: str | None) -> str | None:
    """Return ``value``, falling back to ``SRG_API_KEY`` env var, or ``None``.

    Unlike the previous implementation, an absent api key is allowed — callers
    that want eager bootstrap behaviour MUST still pass one, but server
    processes that bind keys per-request can leave it unset.
    """
    return value or os.environ.get("SRG_API_KEY") or None


def _get_base_url(value: str | None) -> str:
    result = value or os.environ.get("SRG_BASE_URL", _DEFAULT_BASE_URL)
    return result.rstrip("/")


class SRGClient:
    """
    Synchronous SRG SDK client.

    Parameters
    ----------
    api_key:
        Optional default workspace API key (Bearer token). Falls back to
        ``SRG_API_KEY`` env var. When provided, it becomes the default key
        used for every request that doesn't have one bound via
        :meth:`with_api_key` / :meth:`use_api_key`. When omitted, every
        request must run inside an ``api_key`` binding or it will raise
        :class:`SRGError`.
    base_url:
        Base URL for the API gateway. Falls back to ``SRG_BASE_URL`` env var,
        then defaults to ``https://gateway.srgplus.com``.
    timeout:
        HTTP request timeout in seconds (default 30).

    Examples
    --------
    Eager single-key usage (unchanged) — the workspace is fetched up-front::

        client = SRGClient(api_key="srgplus_...")
        profiles = client.hub_profiles.list()

    Per-request key — share one connection pool across many workspaces::

        client = SRGClient()  # no eager bootstrap, no default key

        scoped = client.with_api_key("srgplus_workspace_a")
        scoped.hub_profiles.list()

        with client.use_api_key("srgplus_workspace_b"):
            client.hub_profiles.list()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        self._http = SyncHTTPClient(
            api_key=resolved_key,
            base_url=_get_base_url(base_url),
            timeout=timeout,
        )
        self._workspace_id: str | None = None
        # Eager bootstrap preserves backward-compat: when a default key was
        # provided we fetch workspaces immediately so ``client.workspace_id``
        # works synchronously, just like the old API.
        if resolved_key:
            self._workspace_id = self._bootstrap_workspace()

    def _bootstrap_workspace(self) -> str:
        raw: list[dict[str, object]] = self._http.get("/api/v1/workspaces") or []
        if not raw:
            raise SRGError("No workspaces found for this API key")
        first = raw[0]
        return str(first["id"])

    @property
    def workspace_id(self) -> str:
        """Workspace id for the current default key.

        Triggers a one-shot ``GET /api/v1/workspaces`` call the first time
        it's accessed when no eager bootstrap ran. Requires a key to be
        bound either as a default or via :meth:`use_api_key`.
        """
        if self._workspace_id is None:
            self._workspace_id = self._bootstrap_workspace()
        return self._workspace_id

    def with_api_key(self, api_key: str) -> "_ScopedSRGClient":
        """Return a scoped client that binds ``api_key`` for every request.

        The scoped client shares the same underlying ``httpx.Client`` (and
        therefore the same connection pool) as ``self``. Use this in a
        long-running server that talks to many workspaces.
        """
        return _ScopedSRGClient(self, api_key)

    @contextmanager
    def use_api_key(self, api_key: str) -> Iterator["SRGClient"]:
        """Bind ``api_key`` for the duration of the ``with`` block.

        ::

            with client.use_api_key("srgplus_..."):
                client.hub_profiles.list()
        """
        token = _active_api_key.set(api_key)
        try:
            yield self
        finally:
            _active_api_key.reset(token)

    @cached_property
    def users(self) -> UsersResource:
        return UsersResource(self._http)

    @cached_property
    def invitations(self) -> InvitationsResource:
        return InvitationsResource(self._http)

    @cached_property
    def permissions(self) -> PermissionsResource:
        return PermissionsResource(self._http)

    @cached_property
    def permission_groups(self) -> PermissionGroupsResource:
        return PermissionGroupsResource(self._http)

    @cached_property
    def hub_profiles(self) -> HubProfilesResource:
        return HubProfilesResource(self._http, workspace_id=self._workspace_id)

    @cached_property
    def workspaces(self) -> WorkspacesResource:
        return WorkspacesResource(self._http, workspace_id=self._workspace_id)

    @cached_property
    def assets(self) -> AssetsResource:
        return AssetsResource(self._http)

    @cached_property
    def channels(self) -> ChannelsResource:
        return ChannelsResource(self._http)

    @cached_property
    def contents(self) -> ContentsResource:
        return ContentsResource(self._http)

    def close(self) -> None:
        """Close all underlying HTTP connections."""
        self._http.close()

    def __enter__(self) -> "SRGClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class _ScopedSRGClient:
    """Lightweight wrapper returned by :meth:`SRGClient.with_api_key`.

    Forwards every public attribute access to the parent client while pinning
    the Authorization header to the bound api key. Uses the same connection
    pool and the same resource singletons as the parent — the only thing it
    overrides is the active key in the per-call ``ContextVar``.
    """

    def __init__(self, parent: "SRGClient", api_key: str) -> None:
        self._parent = parent
        self._api_key = api_key

    def __getattr__(self, name: str) -> object:
        # Resource access goes through this — wrap each callable so that the
        # bound key is active for the duration of the call.
        attr = getattr(self._parent, name)
        if name.startswith("_"):
            return attr
        return _BoundResource(attr, self._api_key)

    def with_api_key(self, api_key: str) -> "_ScopedSRGClient":
        return _ScopedSRGClient(self._parent, api_key)

    @contextmanager
    def use_api_key(self, api_key: str) -> Iterator["_ScopedSRGClient"]:
        token = _active_api_key.set(api_key)
        try:
            yield self
        finally:
            _active_api_key.reset(token)


class _BoundResource:
    """Proxy that activates the bound api key on every method call."""

    def __init__(self, target: object, api_key: str) -> None:
        self._target = target
        self._api_key = api_key

    def __getattr__(self, name: str) -> object:
        attr = getattr(self._target, name)
        if not callable(attr):
            return attr

        api_key = self._api_key

        def wrapper(*args: object, **kwargs: object) -> object:
            token = _active_api_key.set(api_key)
            try:
                return attr(*args, **kwargs)
            finally:
                _active_api_key.reset(token)

        return wrapper


class AsyncSRGClient:
    """
    Asynchronous SRG SDK client (identical API to :class:`SRGClient` but all
    methods are coroutines).

    The async client never bootstraps the workspace eagerly: ``workspace_id``
    is fetched lazily the first time it is awaited via
    :meth:`get_workspace_id`. This avoids the previous
    ``AttributeError`` when async users accessed ``client.workspace_id``.

    Examples
    --------
    ::

        async with AsyncSRGClient(api_key="srgplus_...") as client:
            profiles = await client.hub_profiles.list()
            ws_id = await client.get_workspace_id()

        # multi-tenant server pattern
        async with AsyncSRGClient() as client:
            async with client.use_api_key("srgplus_..."):
                profiles = await client.hub_profiles.list()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        self._http = AsyncHTTPClient(
            api_key=resolved_key,
            base_url=_get_base_url(base_url),
            timeout=timeout,
        )
        self._workspace_id: str | None = None

    async def _bootstrap_workspace(self) -> str:
        raw: list[dict[str, object]] = (
            await self._http.get("/api/v1/workspaces") or []
        )
        if not raw:
            raise SRGError("No workspaces found for this API key")
        first = raw[0]
        return str(first["id"])

    async def get_workspace_id(self) -> str:
        """Return the workspace id, fetching it lazily on first access."""
        if self._workspace_id is None:
            self._workspace_id = await self._bootstrap_workspace()
        return self._workspace_id

    @property
    def workspace_id(self) -> str | None:
        """The cached workspace id, or ``None`` if not yet fetched.

        Use :meth:`get_workspace_id` to trigger the fetch.
        """
        return self._workspace_id

    def with_api_key(self, api_key: str) -> "_ScopedAsyncSRGClient":
        """Return a scoped client that binds ``api_key`` for every request."""
        return _ScopedAsyncSRGClient(self, api_key)

    @asynccontextmanager
    async def use_api_key(self, api_key: str) -> AsyncIterator["AsyncSRGClient"]:
        """Async context manager that binds ``api_key`` for the block."""
        token = _active_api_key.set(api_key)
        try:
            yield self
        finally:
            _active_api_key.reset(token)

    @cached_property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self._http)

    @cached_property
    def invitations(self) -> AsyncInvitationsResource:
        return AsyncInvitationsResource(self._http)

    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        return AsyncPermissionsResource(self._http)

    @cached_property
    def permission_groups(self) -> AsyncPermissionGroupsResource:
        return AsyncPermissionGroupsResource(self._http)

    @cached_property
    def hub_profiles(self) -> AsyncHubProfilesResource:
        return AsyncHubProfilesResource(self._http)

    @cached_property
    def workspaces(self) -> AsyncWorkspacesResource:
        return AsyncWorkspacesResource(self._http)

    @cached_property
    def assets(self) -> AsyncAssetsResource:
        return AsyncAssetsResource(self._http)

    @cached_property
    def channels(self) -> AsyncChannelsResource:
        return AsyncChannelsResource(self._http)

    @cached_property
    def contents(self) -> AsyncContentsResource:
        return AsyncContentsResource(self._http)

    async def aclose(self) -> None:
        """Close all underlying HTTP connections."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncSRGClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()


class _ScopedAsyncSRGClient:
    """Async counterpart to :class:`_ScopedSRGClient`."""

    def __init__(self, parent: "AsyncSRGClient", api_key: str) -> None:
        self._parent = parent
        self._api_key = api_key

    def __getattr__(self, name: str) -> object:
        attr = getattr(self._parent, name)
        if name.startswith("_"):
            return attr
        return _BoundAsyncResource(attr, self._api_key)

    def with_api_key(self, api_key: str) -> "_ScopedAsyncSRGClient":
        return _ScopedAsyncSRGClient(self._parent, api_key)

    @asynccontextmanager
    async def use_api_key(
        self, api_key: str
    ) -> AsyncIterator["_ScopedAsyncSRGClient"]:
        token = _active_api_key.set(api_key)
        try:
            yield self
        finally:
            _active_api_key.reset(token)

    async def __aenter__(self) -> "_ScopedAsyncSRGClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._parent.aclose()


class _BoundAsyncResource:
    """Proxy that activates the bound api key for sync- and async-method calls."""

    def __init__(self, target: object, api_key: str) -> None:
        self._target = target
        self._api_key = api_key

    def __getattr__(self, name: str) -> object:
        attr = getattr(self._target, name)
        if not callable(attr):
            return attr

        api_key = self._api_key

        async def async_wrapper(*args: object, **kwargs: object) -> object:
            token = _active_api_key.set(api_key)
            try:
                return await attr(*args, **kwargs)
            finally:
                _active_api_key.reset(token)

        def sync_wrapper(*args: object, **kwargs: object) -> object:
            token = _active_api_key.set(api_key)
            try:
                return attr(*args, **kwargs)
            finally:
                _active_api_key.reset(token)

        # Best-effort detection: async resource methods are coroutine
        # functions, sync helpers (e.g. pagination iterators) are not.
        import inspect

        if inspect.iscoroutinefunction(attr):
            return async_wrapper
        return sync_wrapper
