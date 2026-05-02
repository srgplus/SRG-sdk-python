<a id="srg._client"></a>

# srg.\_client

## Per-request API keys (since 0.2.0)

Both `SRGClient` and `AsyncSRGClient` support binding a workspace API key
per call instead of per client. This lets one process share a single
`httpx` connection pool across any number of workspaces — useful for
hosted MCP servers and multi-tenant agents.

| Helper | Description |
|--------|-------------|
| `SRGClient(api_key=None)` | Construct without a default key — every request must run inside a binding. |
| `client.with_api_key(key)` | Return a scoped clone that pins `key` for every call (option A). |
| `client.use_api_key(key)` | Sync context manager — binds `key` for the `with` block (option C). |
| `await async_client.use_api_key(key)` | Async context manager equivalent. |
| `async_client.with_api_key(key)` | Scoped clone (async). |
| `await async_client.get_workspace_id()` | Lazy bootstrap; the async client never fetches workspaces eagerly. |

Example:

```python
client = SRGClient()  # no eager bootstrap

scoped = client.with_api_key("srgplus_workspace_a")
scoped.hub_profiles.list()

with client.use_api_key("srgplus_workspace_b"):
    client.hub_profiles.list()
```

Backward compatibility: if you pass `SRGClient(api_key="srgplus_...")` (or
set `SRG_API_KEY`), that key becomes the default for the lifetime of the
client and `client.workspace_id` is fetched eagerly — exactly as it did in
0.1.x.

> **Multi-tenant gotcha — `workspace_id` is `None` without a default key.**
> When `SRGClient()` is constructed without an `api_key` (and no
> `SRG_API_KEY` env var is set), there is no eager bootstrap, so
> `client.workspace_id` stays `None`. Resource methods that build URLs
> from the cached id (e.g. `client.hub_profiles.list()` →
> `/api/v1/workspaces/None/...`) will fail. This is by design: the
> per-request flow via `with_api_key()` / `use_api_key()` works because
> the upstream HTTP layer carries the auth and the resource methods that
> participate in that flow accept a workspace id explicitly (e.g.
> `scoped.workspaces.list_actions("ws-id")`). If you need
> `client.hub_profiles`-style attribute access in a multi-tenant process,
> construct one client per tenant with their key, or pass the workspace
> id through the resource call.

<a id="srg._client.SRGClient"></a>

## SRGClient Objects

```python
class SRGClient()
```

Synchronous SRG SDK client.

Parameters
----------
api_key:
    Optional default workspace API key (Bearer token). Falls back to
    ``SRG_API_KEY`` env var. When omitted, every request must run inside a
    ``with_api_key`` / ``use_api_key`` binding.
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

    # multi-tenant server pattern
    pool = SRGClient()
    with pool.use_api_key("srgplus_other_workspace"):
        pool.hub_profiles.list()

<a id="srg._client.SRGClient.users"></a>

#### users

```python
@cached_property
def users() -> UsersResource
```

Provides a cached property that returns a `UsersResource` instance. This allows

on-demand initialization and caching of the resource, optimizing repeated access.

**Returns**:

`UsersResource`: An instance of `UsersResource` initialized with the HTTP client.

<a id="srg._client.SRGClient.invitations"></a>

#### invitations

```python
@cached_property
def invitations() -> InvitationsResource
```

Provides a cached property that returns an instance of InvitationsResource.

This property lazily initializes and caches an instance of
InvitationsResource, which utilizes the existing HTTP client instance
to perform operations related to invitations.

**Returns**:

`InvitationsResource`: A cached instance of InvitationsResource.

<a id="srg._client.SRGClient.permissions"></a>

#### permissions

```python
@cached_property
def permissions() -> PermissionsResource
```

Provides a cached property that returns a PermissionsResource instance.

The property caches the computed value after its first access to improve
performance and avoid repeated computations.

**Returns**:

`PermissionsResource`: An instance of PermissionsResource associated with the current
HTTP session.

<a id="srg._client.SRGClient.permission_groups"></a>

#### permission\_groups

```python
@cached_property
def permission_groups() -> PermissionGroupsResource
```

Returns a resource object for handling permission groups.

This property provides access to the PermissionGroupsResource, which facilitates
operations related to managing permission groups in the system.

**Returns**:

`PermissionGroupsResource`: A PermissionGroupsResource instance initialized with the current HTTP
connection.

<a id="srg._client.SRGClient.hub_profiles"></a>

#### hub\_profiles

```python
@cached_property
def hub_profiles() -> HubProfilesResource
```

Provides cached access to the HubProfilesResource associated with the workspace ID.

This property initializes and returns an instance of HubProfilesResource, ensuring that
the resource is created only once and reused on subsequent accesses.

**Returns**:

`HubProfilesResource`: The HubProfilesResource instance associated with the current workspace ID.

<a id="srg._client.SRGClient.workspaces"></a>

#### workspaces

```python
@cached_property
def workspaces() -> WorkspacesResource
```

Provides a cached property that initializes and returns a `WorkspacesResource`

object. This allows lazy-fetching of the resource and caches the result for
subsequent access.

**Returns**:

`WorkspacesResource`: An instance of `WorkspacesResource` initialized with the `_http`
attribute.

<a id="srg._client.SRGClient.assets"></a>

#### assets

```python
@cached_property
def assets() -> AssetsResource
```

Provides a cached property that initializes and returns an instance of

the AssetsResource class. The property ensures that the instance is
created only once and is then cached for subsequent accesses.

**Returns**:

`AssetsResource`: An instance of the AssetsResource class initialized with
the current HTTP session.

<a id="srg._client.SRGClient.channels"></a>

#### channels

```python
@cached_property
def channels() -> ChannelsResource
```

A cached property that returns an instance of ChannelsResource. This property

is computed on the first access and then cached for subsequent accesses, ensuring
efficient and reusable access to the ChannelsResource object.

**Returns**:

`ChannelsResource`: An instance of ChannelsResource.

<a id="srg._client.SRGClient.contents"></a>

#### contents

```python
@cached_property
def contents() -> ContentsResource
```

Provides access to the ContentsResource, encapsulating its initialization and

ensuring it is created only once through caching.

**Returns**:

`ContentsResource`: A new or cached instance of ``ContentsResource`` associated with the corresponding
HTTP client.

<a id="srg._client.SRGClient.close"></a>

#### close

```python
def close() -> None
```

Close all underlying HTTP connections.

<a id="srg._client.AsyncSRGClient"></a>

## AsyncSRGClient Objects

```python
class AsyncSRGClient()
```

Asynchronous SRG SDK client (identical API to :class:`SRGClient`
but all methods are coroutines).

Unlike :class:`SRGClient`, the async client never fetches workspaces in its
constructor. Use ``await client.get_workspace_id()`` to fire the bootstrap
lazily; ``client.workspace_id`` returns the cached value (or ``None`` if it
hasn't been fetched yet) without raising.

Example
-------
::

    async with AsyncSRGClient(api_key="srgplus_...") as client:
        profiles = await client.hub_profiles.list()
        ws_id = await client.get_workspace_id()

<a id="srg._client.AsyncSRGClient.users"></a>

#### users

```python
@cached_property
def users() -> AsyncUsersResource
```

Returns an instance of AsyncUsersResource for accessing user-related resources.

The method lazily instantiates an AsyncUsersResource object, which interacts
with user-related endpoints of the API. Cached on the property level to avoid
redundant creation of instances.

**Returns**:

`AsyncUsersResource`: An instance of AsyncUsersResource.

<a id="srg._client.AsyncSRGClient.invitations"></a>

#### invitations

```python
@cached_property
def invitations() -> AsyncInvitationsResource
```

Provides a cached property for accessing the asynchronous invitations resource

associated with the current object. This property initializes the resource only
on demand and caches the result for future access.

**Returns**:

An asynchronous instance of InvitationsResource, providing access
to invitations-related operations.

<a id="srg._client.AsyncSRGClient.permissions"></a>

#### permissions

```python
@cached_property
def permissions() -> AsyncPermissionsResource
```

Provides access to permissions resource associated with the current instance.

This method returns an instance of `AsyncPermissionsResource` which allows
interaction with permissions data in an asynchronous manner. The returned
resource uses the current HTTP session for communication.

**Returns**:

`AsyncPermissionsResource`: An instance of `AsyncPermissionsResource` configured with the current
HTTP session for asynchronous permissions management.

<a id="srg._client.AsyncSRGClient.permission_groups"></a>

#### permission\_groups

```python
@cached_property
def permission_groups() -> AsyncPermissionGroupsResource
```

Provides a cached property that returns an instance of AsyncPermissionGroupsResource.

This property initializes and returns an `AsyncPermissionGroupsResource` object
using the provided HTTP client. The result is cached to avoid redundant
initializations, improving performance for subsequent accesses.

**Returns**:

`AsyncPermissionGroupsResource`: An instance of AsyncPermissionGroupsResource initialized with the HTTP client.

<a id="srg._client.AsyncSRGClient.hub_profiles"></a>

#### hub\_profiles

```python
@cached_property
def hub_profiles() -> AsyncHubProfilesResource
```

Provides access to hub profile resources in an asynchronous manner.

This property allows lazy initialization and caching of an
`AsyncHubProfilesResource` instance. Subsequent accesses to this property
return the cached instance.

**Returns**:

`AsyncHubProfilesResource`: An instance of `AsyncHubProfilesResource` initialized with the
current asynchronous HTTP client.

<a id="srg._client.AsyncSRGClient.workspaces"></a>

#### workspaces

```python
@cached_property
def workspaces() -> AsyncWorkspacesResource
```

Provides a cached property for accessing an instance of AsyncWorkspacesResource.

The method utilizes the `functools.cached_property` decorator to ensure that the
`AsyncWorkspacesResource` instance is created only once and reused on subsequent
accesses. This is useful when the initialization of the resource is computationally
expensive or requires network requests.

**Returns**:

`AsyncWorkspacesResource`: An instance of AsyncWorkspacesResource associated with the current HTTP
client.

<a id="srg._client.AsyncSRGClient.assets"></a>

#### assets

```python
@cached_property
def assets() -> AsyncAssetsResource
```

Provides a cached property that initializes and returns an instance of

AsyncAssetsResource. The value is computed only once, and subsequent
accesses return the cached result.

**Returns**:

`AsyncAssetsResource`: An instance of AsyncAssetsResource.

<a id="srg._client.AsyncSRGClient.channels"></a>

#### channels

```python
@cached_property
def channels() -> AsyncChannelsResource
```

Provides a cached property that returns an instance of AsyncChannelsResource.

**Returns**:

`AsyncChannelsResource`: An instance of AsyncChannelsResource initialized with the current
HTTP client.

<a id="srg._client.AsyncSRGClient.contents"></a>

#### contents

```python
@cached_property
def contents() -> AsyncContentsResource
```

A cached property that provides access to an `AsyncContentsResource` instance.

This property lazily initializes the `AsyncContentsResource` object upon first
access and caches the result for subsequent accesses, improving efficiency for
repeated calls.

**Returns**:

`AsyncContentsResource`: An instance of AsyncContentsResource for handling asynchronous
content-related operations.

<a id="srg._client.AsyncSRGClient.aclose"></a>

#### aclose

```python
async def aclose() -> None
```

Close all underlying HTTP connections.

