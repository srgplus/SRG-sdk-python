import os
from functools import cached_property

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.exceptions import AuthenticationError, SRGError
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


def _resolve_keys(api_keys: list[str] | None) -> list[str]:
    keys: list[str] = list(api_keys or [])
    if not keys:
        env_val = os.environ.get("SRG_API_KEYS", "")
        keys = [k.strip() for k in env_val.split(",") if k.strip()]
    if not keys:
        raise SRGError(
            "api_keys must be provided either as a parameter or "
            "via the SRG_API_KEYS environment variable (comma-separated)."
        )
    return keys


def _get_base_url(value: str | None) -> str:
    result = value or os.environ.get("SRG_BASE_URL", _DEFAULT_BASE_URL)
    return result.rstrip("/")


class SRGClient:
    """
    Synchronous SRG SDK client.

    The client maintains an internal **registry** — a mapping of
    ``workspace_id → SyncHTTPClient`` — built at construction time by
    bootstrapping each supplied API key.  Every resource method that
    talks to the API requires an explicit ``workspace_id`` argument;
    the client looks up the corresponding HTTP client in the registry
    and uses it for that call.  This lets a single ``SRGClient``
    instance serve multiple workspaces concurrently while keeping each
    request isolated to the correct credentials.

    Keys that cannot be resolved to a workspace (e.g. invalid or
    revoked keys) are silently skipped.  If *no* key resolves to a
    workspace the constructor raises :class:`~srg.exceptions.SRGError`.

    Parameters
    ----------
    api_keys:
        One or more workspace API keys.  Falls back to the
        ``SRG_API_KEYS`` environment variable (comma-separated list).
    base_url:
        API gateway base URL.  Falls back to ``SRG_BASE_URL`` env var,
        then ``https://gateway.srgplus.com``.
    timeout:
        HTTP request timeout in seconds (default 30).

    Examples
    --------
    Single workspace::

        client = SRGClient(api_keys=["srgplus_..."])
        profiles = client.hub_profiles.list(workspace_id="ws-uuid-1")

    Multiple workspaces from environment::

        # SRG_API_KEYS=srgplus_ws1,srgplus_ws2
        client = SRGClient()
        profiles = client.hub_profiles.list(workspace_id="ws-uuid-1")
        other    = client.hub_profiles.list(workspace_id="ws-uuid-2")

    Inspect registered workspaces::

        configured = client.workspaces.list_configured()
    """

    def __init__(
        self,
        *,
        api_keys: list[str] | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        keys = _resolve_keys(api_keys)
        base = _get_base_url(base_url)
        self._registry: dict[str, SyncHTTPClient] = {}
        for key in keys:
            http = SyncHTTPClient(api_key=key, base_url=base, timeout=timeout)
            try:
                raw: list = http.get("/api/v1/workspaces") or []
            except AuthenticationError:
                continue  # invalid key — skip silently
            if not raw:
                continue  # key has no accessible workspace — skip silently
            ws_id = str(raw[0]["id"])
            self._registry[ws_id] = http
        if not self._registry:
            raise SRGError("No workspaces found for any of the provided API keys")

    @property
    def workspace_ids(self) -> list[str]:
        """Return the list of workspace IDs accessible with the provided API keys."""
        return list(self._registry)

    @cached_property
    def users(self) -> UsersResource:
        """
        Provides a cached property that returns a `UsersResource` instance. This allows
        on-demand initialization and caching of the resource, optimizing repeated access.

        :return: An instance of `UsersResource` initialized with the HTTP client.
        :rtype: UsersResource
        """
        return UsersResource(self._registry)

    @cached_property
    def invitations(self) -> InvitationsResource:
        """
        Provides a cached property that returns an instance of InvitationsResource.

        This property lazily initializes and caches an instance of
        InvitationsResource, which utilizes the existing HTTP client instance
        to perform operations related to invitations.

        :return: A cached instance of InvitationsResource.
        :rtype: InvitationsResource
        """
        return InvitationsResource(self._registry)

    @cached_property
    def permissions(self) -> PermissionsResource:
        """
        Provides a cached property that returns a PermissionsResource instance.

        The property caches the computed value after its first access to improve
        performance and avoid repeated computations.

        :return: An instance of PermissionsResource associated with the current
            HTTP session.
        :rtype: PermissionsResource
        """
        return PermissionsResource(self._registry)

    @cached_property
    def permission_groups(self) -> PermissionGroupsResource:
        """
        Returns a resource object for handling permission groups.

        This property provides access to the PermissionGroupsResource, which facilitates
        operations related to managing permission groups in the system.

        :return: A PermissionGroupsResource instance initialized with the current HTTP
            connection.
        :rtype: PermissionGroupsResource
        """
        return PermissionGroupsResource(self._registry)

    @cached_property
    def hub_profiles(self) -> HubProfilesResource:
        """
        Provides cached access to the HubProfilesResource associated with the workspace ID.

        This property initializes and returns an instance of HubProfilesResource, ensuring that
        the resource is created only once and reused on subsequent accesses.

        :return: The HubProfilesResource instance associated with the current workspace ID.
        :rtype: HubProfilesResource
        """
        return HubProfilesResource(self._registry)

    @cached_property
    def workspaces(self) -> WorkspacesResource:
        """
        Provides a cached property that initializes and returns a `WorkspacesResource`
        object. This allows lazy-fetching of the resource and caches the result for
        subsequent access.

        :return: An instance of `WorkspacesResource` initialized with the `_http`
            attribute.
        :rtype: WorkspacesResource
        """
        return WorkspacesResource(self._registry)

    @cached_property
    def assets(self) -> AssetsResource:
        """
        Provides a cached property that initializes and returns an instance of
        the AssetsResource class. The property ensures that the instance is
        created only once and is then cached for subsequent accesses.

        :return: An instance of the AssetsResource class initialized with
            the current HTTP session.
        :rtype: AssetsResource
        """
        return AssetsResource(self._registry)

    @cached_property
    def channels(self) -> ChannelsResource:
        """
        A cached property that returns an instance of ChannelsResource. This property
        is computed on the first access and then cached for subsequent accesses, ensuring
        efficient and reusable access to the ChannelsResource object.

        :return: An instance of ChannelsResource.
        :rtype: ChannelsResource
        """
        return ChannelsResource(self._registry)

    @cached_property
    def contents(self) -> ContentsResource:
        """
        Provides access to the ContentsResource, encapsulating its initialization and
        ensuring it is created only once through caching.

        :cached_property:
            A decorator that transforms the method into a read-only property, whose
            value is computed once and then cached for subsequent access.

        :return: A new or cached instance of ``ContentsResource`` associated with the corresponding
            HTTP client.
        :rtype: ContentsResource
        """
        return ContentsResource(self._registry)

    def close(self) -> None:
        for http in self._registry.values():
            http.close()

    def __enter__(self) -> "SRGClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncSRGClient:
    """
    Asynchronous SRG SDK client.

    Identical API to :class:`SRGClient` but all resource methods are
    coroutines.  The internal **registry** (``workspace_id →
    AsyncHTTPClient``) is populated during bootstrap, which happens
    inside ``__aenter__``.  Always use this client as an async context
    manager, or call ``await client.bootstrap()`` before accessing
    resources.

    Keys that cannot be resolved to a workspace (e.g. invalid or
    revoked keys) are silently skipped.  If *no* key resolves to a
    workspace, :meth:`bootstrap` raises :class:`~srg.exceptions.SRGError`.

    Parameters
    ----------
    api_keys:
        One or more workspace API keys.  Falls back to the
        ``SRG_API_KEYS`` environment variable (comma-separated list).
    base_url:
        API gateway base URL.  Falls back to ``SRG_BASE_URL`` env var,
        then ``https://gateway.srgplus.com``.
    timeout:
        HTTP request timeout in seconds (default 30).

    Examples
    --------
    ::

        async with AsyncSRGClient(api_keys=["srgplus_ws1", "srgplus_ws2"]) as client:
            profiles = await client.hub_profiles.list(workspace_id="ws-uuid-1")
            configured = await client.workspaces.list_configured()
    """

    def __init__(
        self,
        *,
        api_keys: list[str] | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._raw_keys = _resolve_keys(api_keys)
        self._base = _get_base_url(base_url)
        self._timeout = timeout
        self._registry: dict[str, AsyncHTTPClient] = {}

    async def bootstrap(self) -> None:
        """Populate the registry by resolving each API key to its workspace.

        Idempotent — subsequent calls are no-ops once the registry is built.
        Keys that return no workspaces are silently skipped.
        """
        if self._registry:
            return
        for key in self._raw_keys:
            http = AsyncHTTPClient(
                api_key=key, base_url=self._base, timeout=self._timeout
            )
            try:
                raw: list = await http.get("/api/v1/workspaces") or []
            except AuthenticationError:
                continue  # invalid key — skip silently
            if not raw:
                continue
            ws_id = str(raw[0]["id"])
            self._registry[ws_id] = http
        if not self._registry:
            raise SRGError("No workspaces found for any of the provided API keys")

    @property
    def workspace_ids(self) -> list[str]:
        """Return the list of workspace IDs accessible with the provided API keys."""
        return list(self._registry)

    @cached_property
    def users(self) -> AsyncUsersResource:
        """
        Returns an instance of AsyncUsersResource for accessing user-related resources.

        The method lazily instantiates an AsyncUsersResource object, which interacts
        with user-related endpoints of the API. Cached on the property level to avoid
        redundant creation of instances.

        :return: An instance of AsyncUsersResource.
        :rtype: AsyncUsersResource
        """
        return AsyncUsersResource(self._registry)

    @cached_property
    def invitations(self) -> AsyncInvitationsResource:
        """
        Provides a cached property for accessing the asynchronous invitations resource
        associated with the current object. This property initializes the resource only
        on demand and caches the result for future access.

        :return: An asynchronous instance of InvitationsResource, providing access
            to invitations-related operations.
        """
        return AsyncInvitationsResource(self._registry)

    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        """
        Provides access to permissions resource associated with the current instance.

        This method returns an instance of `AsyncPermissionsResource` which allows
        interaction with permissions data in an asynchronous manner. The returned
        resource uses the current HTTP session for communication.

        :return: An instance of `AsyncPermissionsResource` configured with the current
            HTTP session for asynchronous permissions management.
        :rtype: AsyncPermissionsResource
        """
        return AsyncPermissionsResource(self._registry)

    @cached_property
    def permission_groups(self) -> AsyncPermissionGroupsResource:
        """
        Provides a cached property that returns an instance of AsyncPermissionGroupsResource.

        This property initializes and returns an `AsyncPermissionGroupsResource` object
        using the provided HTTP client. The result is cached to avoid redundant
        initializations, improving performance for subsequent accesses.

        :return: An instance of AsyncPermissionGroupsResource initialized with the HTTP client.
        :rtype: AsyncPermissionGroupsResource
        """
        return AsyncPermissionGroupsResource(self._registry)

    @cached_property
    def hub_profiles(self) -> AsyncHubProfilesResource:
        """
        Provides access to hub profile resources in an asynchronous manner.

        This property allows lazy initialization and caching of an
        `AsyncHubProfilesResource` instance. Subsequent accesses to this property
        return the cached instance.

        :return: An instance of `AsyncHubProfilesResource` initialized with the
            current asynchronous HTTP client.
        :rtype: AsyncHubProfilesResource
        """
        return AsyncHubProfilesResource(self._registry)

    @cached_property
    def workspaces(self) -> AsyncWorkspacesResource:
        """
        Provides a cached property for accessing an instance of AsyncWorkspacesResource.

        The method utilizes the `functools.cached_property` decorator to ensure that the
        `AsyncWorkspacesResource` instance is created only once and reused on subsequent
        accesses. This is useful when the initialization of the resource is computationally
        expensive or requires network requests.

        :return: An instance of AsyncWorkspacesResource associated with the current HTTP
            client.
        :rtype: AsyncWorkspacesResource
        """
        return AsyncWorkspacesResource(self._registry)

    @cached_property
    def assets(self) -> AsyncAssetsResource:
        """
        Provides a cached property that initializes and returns an instance of
        AsyncAssetsResource. The value is computed only once, and subsequent
        accesses return the cached result.

        :return: An instance of AsyncAssetsResource.
        :rtype: AsyncAssetsResource
        """
        return AsyncAssetsResource(self._registry)

    @cached_property
    def channels(self) -> AsyncChannelsResource:
        """
        Provides a cached property that returns an instance of AsyncChannelsResource.

        :rtype: AsyncChannelsResource
        :return: An instance of AsyncChannelsResource initialized with the current
            HTTP client.
        """
        return AsyncChannelsResource(self._registry)

    @cached_property
    def contents(self) -> AsyncContentsResource:
        """
        A cached property that provides access to an `AsyncContentsResource` instance.

        This property lazily initializes the `AsyncContentsResource` object upon first
        access and caches the result for subsequent accesses, improving efficiency for
        repeated calls.

        :return: An instance of AsyncContentsResource for handling asynchronous
                 content-related operations.
        :rtype: AsyncContentsResource
        """
        return AsyncContentsResource(self._registry)

    async def aclose(self) -> None:
        for http in self._registry.values():
            await http.aclose()

    async def __aenter__(self) -> "AsyncSRGClient":
        await self.bootstrap()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
