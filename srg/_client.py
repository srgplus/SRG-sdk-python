import os
from functools import cached_property

from srg._http import AsyncHTTPClient, SyncHTTPClient
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


def _get_api_key(value: str | None) -> str:
    result = value or os.environ.get("SRG_API_KEY", "")
    if not result:
        raise SRGError(
            "api_key must be provided either as a parameter or "
            "via the SRG_API_KEY environment variable."
        )
    return result


def _get_base_url(value: str | None) -> str:
    result = value or os.environ.get("SRG_BASE_URL", _DEFAULT_BASE_URL)
    return result.rstrip("/")


class SRGClient:
    """
    Synchronous SRG SDK client.

    Parameters
    ----------
    api_key:
        Workspace API key (Bearer token).  Falls back to ``SRG_API_KEY`` env var.
    base_url:
        Base URL for the API gateway.  Falls back to ``SRG_BASE_URL`` env var,
        then defaults to ``https://gateway.srgplus.com``.
    timeout:
        HTTP request timeout in seconds (default 30).

    Example
    -------
    ::

        client = SRGClient(api_key="srgplus_...")
        profiles = client.hub_profiles.list()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._http = SyncHTTPClient(
            api_key=_get_api_key(api_key),
            base_url=_get_base_url(base_url),
            timeout=timeout,
        )
        raw: list = self._http.get("/api/v1/workspaces") or []
        if not raw:
            raise SRGError("No workspaces found for this API key")
        self.workspace_id: str = raw[0]["id"]

    @cached_property
    def users(self) -> UsersResource:
        """
        Provides a cached property that returns a `UsersResource` instance. This allows
        on-demand initialization and caching of the resource, optimizing repeated access.

        :return: An instance of `UsersResource` initialized with the HTTP client.
        :rtype: UsersResource
        """
        return UsersResource(self._http)

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
        return InvitationsResource(self._http)

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
        return PermissionsResource(self._http)

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
        return PermissionGroupsResource(self._http)

    @cached_property
    def hub_profiles(self) -> HubProfilesResource:
        """
        Provides cached access to the HubProfilesResource associated with the workspace ID.

        This property initializes and returns an instance of HubProfilesResource, ensuring that
        the resource is created only once and reused on subsequent accesses.

        :return: The HubProfilesResource instance associated with the current workspace ID.
        :rtype: HubProfilesResource
        """
        return HubProfilesResource(self._http, workspace_id=self.workspace_id)

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
        return WorkspacesResource(self._http)

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
        return AssetsResource(self._http)

    @cached_property
    def channels(self) -> ChannelsResource:
        """
        A cached property that returns an instance of ChannelsResource. This property
        is computed on the first access and then cached for subsequent accesses, ensuring
        efficient and reusable access to the ChannelsResource object.

        :return: An instance of ChannelsResource.
        :rtype: ChannelsResource
        """
        return ChannelsResource(self._http)

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
        return ContentsResource(self._http)

    def close(self) -> None:
        """Close all underlying HTTP connections."""
        self._http.close()

    def __enter__(self) -> "SRGClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncSRGClient:
    """
    Asynchronous SRG SDK client (identical API to :class:`SRGClient`
    but all methods are coroutines).

    Example
    -------
    ::

        async with AsyncSRGClient(api_key="srgplus_...") as client:
            profiles = await client.hub_profiles.list()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._http = AsyncHTTPClient(
            api_key=_get_api_key(api_key),
            base_url=_get_base_url(base_url),
            timeout=timeout,
        )

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
        return AsyncUsersResource(self._http)

    @cached_property
    def invitations(self) -> AsyncInvitationsResource:
        """
        Provides a cached property for accessing the asynchronous invitations resource
        associated with the current object. This property initializes the resource only
        on demand and caches the result for future access.

        :return: An asynchronous instance of InvitationsResource, providing access
            to invitations-related operations.
        """
        return AsyncInvitationsResource(self._http)

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
        return AsyncPermissionsResource(self._http)

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
        return AsyncPermissionGroupsResource(self._http)

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
        return AsyncHubProfilesResource(self._http)

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
        return AsyncWorkspacesResource(self._http)

    @cached_property
    def assets(self) -> AsyncAssetsResource:
        """
        Provides a cached property that initializes and returns an instance of
        AsyncAssetsResource. The value is computed only once, and subsequent
        accesses return the cached result.

        :return: An instance of AsyncAssetsResource.
        :rtype: AsyncAssetsResource
        """
        return AsyncAssetsResource(self._http)

    @cached_property
    def channels(self) -> AsyncChannelsResource:
        """
        Provides a cached property that returns an instance of AsyncChannelsResource.

        :rtype: AsyncChannelsResource
        :return: An instance of AsyncChannelsResource initialized with the current
            HTTP client.
        """
        return AsyncChannelsResource(self._http)

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
        return AsyncContentsResource(self._http)

    async def aclose(self) -> None:
        """Close all underlying HTTP connections."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncSRGClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
