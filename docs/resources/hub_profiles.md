<a id="srg.resources.hub_profiles"></a>

# srg.resources.hub\_profiles

<a id="srg.resources.hub_profiles.HubProfilesResource"></a>

## HubProfilesResource Objects

```python
class HubProfilesResource()
```

<a id="srg.resources.hub_profiles.HubProfilesResource.create"></a>

#### create

```python
def create(
    *,
    name: str,
    user_name: str,
    sub_name: str | None = None,
    description: str | None = None,
    primary_url: str | None = None,
    availability_level: AvailabilityLevel = "Public",
    app_clip_on: bool = False,
    buttons: list[ActionButtonUpsert] | None = None,
    avatar_image: str | Path | None = None,
    cover_image: str | Path | None = None,
    avatar_extension: str | None = None,
    cover_extension: str | None = None,
    workspace_id: str | None = None,
    widgets: list[dict] | None = None
) -> GetHubProfile | HubProfileSignedUrls
```

Create a new hub profile.

Creates a hub profile inside the workspace.

**Auto-upload mode** — pass ``avatar_image`` and/or ``cover_image`` as
a local file path or an ``http(s)://`` URL. The SDK will obtain signed
upload URLs from the API, upload the images to S3, then fetch and
return the fully populated :class:`~srg.schemas.hub_profile.GetHubProfile`
(with ``avatar``/``cover`` already set).

**Manual mode** — pass ``avatar_extension`` and/or ``cover_extension``
instead. The API returns
:class:`~srg.schemas.hub_profile.HubProfileSignedUrls` containing the
signed URLs so you can upload the images yourself.

**Arguments**:

- `name` - Display name for the hub profile.
- `user_name` - Unique username / URL slug for the hub profile.
- `sub_name` - Optional subtitle shown below the name.
- `description` - Optional text description.
- `primary_url` - Optional external URL shown on the profile.
- `availability_level` - Visibility — ``"Public"`` (default) or
  ``"Private"``.
- `app_clip_on` - Whether to enable iOS App Clip. Defaults to False.
- `buttons` - List of action buttons to display on the profile page.
- `avatar_image` - Local path or ``http(s)://`` URL of the avatar image.
  The extension is derived automatically. Triggers auto-upload.
- `cover_image` - Local path or ``http(s)://`` URL of the cover image.
  The extension is derived automatically. Triggers auto-upload.
- `avatar_extension` - File extension for the avatar image (e.g.
  ``"jpg"``). Used in manual mode when ``avatar_image`` is not
  provided.
- `cover_extension` - File extension for the cover image. Used in manual
  mode when ``cover_image`` is not provided.
- `workspace_id` - Workspace to create the profile in. Uses the client's
  default workspace if omitted.
- `widgets` - Profile widget configuration objects.
  

**Returns**:

  :class:`~srg.schemas.hub_profile.GetHubProfile` when
  ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
  :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
  (manual mode).
  

**Example**:

```python
# Auto-upload — pass a local path or external URL
client = SRGClient(api_key="srgplus_your_key")
profile = client.hub_profiles.create(
    name="Acme Academy",
    user_name="acme-academy",
    description="Official learning hub for Acme Corp employees.",
    avatar_image="/path/to/avatar.jpg",
    cover_image="https://example.com/cover.png",
)
# profile is GetHubProfile with avatar and cover already populated
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    avatar=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/avatars/acme-academy.jpg",
            extension="jpg",
        ),
        modified="2025-06-01T10:00:00Z",
    ),
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-academy.png",
            extension="png",
        ),
        modified="2025-06-01T10:00:00Z",
    ),
    buttons=[],
    widgets=[],
)
```

<a id="srg.resources.hub_profiles.HubProfilesResource.get"></a>

#### get

```python
def get(hub_profile_id: str) -> GetHubProfile
```

Get a hub profile by ID.

Retrieves the full details of a hub profile, including its name,
username, description, avatar, cover, action buttons, and widgets.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to retrieve.
  

**Returns**:

  GetHubProfile with all profile fields.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
profile = client.hub_profiles.get("01965f7a-0000-7000-8000-000000000002")
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    drive_id=None,
    sub_name=None,
    description="Official learning hub for Acme Corp employees.",
    primary_url=None,
    app_clip_on=False,
    availability_level=0,
    avatar=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/avatars/acme-academy.jpg",
            extension="jpg",
        ),
        modified="2025-06-01T10:00:00Z",
    ),
    cover=None,
    qr_code=HubProfileQrCode(
        target_url="https://app.srgplus.com/acme-academy",
        qr_code_url="https://cdn.srgplus.com/qr/acme-academy.png",
    ),
    buttons=[
        ActionButtonResponse(
            title="Visit Website",
            hidden=False,
            logic=ActionLogicResponse(
                dollar_type="ExternalLink",
                url="https://acme.example.com",
                data=None,
            ),
        )
    ],
    widgets=[],
)
```
<a id="srg.resources.hub_profiles.HubProfilesResource.get_by_username"></a>

#### get\_by\_username

```python
def get_by_username(username: str) -> GetHubProfile
```

Get a hub profile by its username.

Retrieves the full details of a hub profile using its URL slug
instead of its ID. Useful when you only know the public-facing
username of the profile.

**Arguments**:

- `username` - The hub profile's username / URL slug (e.g.
  ``"acme-academy"``).
  

**Returns**:

  GetHubProfile with all profile fields.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
profile = client.hub_profiles.get_by_username("acme-academy")
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    drive_id=None,
    sub_name=None,
    description="Official learning hub for Acme Corp employees.",
    primary_url=None,
    app_clip_on=False,
    availability_level=0,
    avatar=None,
    cover=None,
    qr_code=None,
    buttons=[],
    widgets=[],
)
```
<a id="srg.resources.hub_profiles.HubProfilesResource.list"></a>

#### list

```python
def list() -> builtins.list[MinimalHubProfile]
```

List all hub profiles in the current workspace.

Returns a minimal summary of each hub profile in the workspace
associated with the client's API key.

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
profiles = client.hub_profiles.list()
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=Cover(
            details=CoverDetails(
                url="https://cdn.srgplus.com/avatars/acme-academy.jpg",
                extension="jpg",
            ),
            modified="2025-06-01T10:00:00Z",
        ),
    ),
]
```
<a id="srg.resources.hub_profiles.HubProfilesResource.list_managed"></a>

#### list\_managed

```python
def list_managed() -> builtins.list[MinimalHubProfile]
```

List all hub profiles managed by the current user.

Returns every hub profile for which the current API key user has
an Admin or Editor role. Useful for scoping operations to profiles
the caller can modify.

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
managed = client.hub_profiles.list_managed()
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=None,
    ),
]
```
<a id="srg.resources.hub_profiles.HubProfilesResource.update"></a>

#### update

```python
def update(
    hub_profile_id: str,
    *,
    name: str,
    user_name: str,
    sub_name: str | None = None,
    description: str | None = None,
    primary_url: str | None = None,
    availability_level: AvailabilityLevel = "Public",
    app_clip_on: bool = False,
    buttons: builtins.list[ActionButtonUpsert] | None = None,
    avatar_image: str | Path | None = None,
    cover_image: str | Path | None = None,
    avatar: FileUploadParameters | None = None,
    cover: FileUploadParameters | None = None,
    widgets: builtins.list[dict] | None = None
) -> GetHubProfile | HubProfileSignedUrls
```

Update a hub profile's metadata and images.

Replaces the hub profile's fields with the provided values. All fields
are overwritten.

**Auto-upload mode** — pass ``avatar_image`` and/or ``cover_image`` as
a local file path or an ``http(s)://`` URL. The SDK derives the
extension, requests signed URLs, uploads the images, and returns the
updated :class:`~srg.schemas.hub_profile.GetHubProfile`.

**Manual mode** — pass ``avatar`` and/or ``cover`` as
:class:`~srg.schemas.common.FileUploadParameters`. The API returns
:class:`~srg.schemas.hub_profile.HubProfileSignedUrls` with the signed
URLs so you can upload the images yourself.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to update.
- `name` - New display name.
- `user_name` - New username / URL slug.
- `sub_name` - New subtitle. Pass ``None`` to clear.
- `description` - New description text. Pass ``None`` to clear.
- `primary_url` - New primary external URL. Pass ``None`` to clear.
- `availability_level` - New visibility — ``"Public"`` or ``"Private"``.
- `app_clip_on` - Whether to enable iOS App Clip.
- `buttons` - New list of action buttons. Replaces the existing list.
- `avatar_image` - Local path or ``http(s)://`` URL of the new avatar
  image. Triggers auto-upload.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `avatar` - Avatar upload parameters (manual mode).
- `cover` - Cover upload parameters (manual mode).
- `widgets` - New widget configuration. Replaces the existing widgets.
  

**Returns**:

  :class:`~srg.schemas.hub_profile.GetHubProfile` when
  ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
  :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
  (manual mode).
  

**Example**:

```python
# Auto-upload — pass a local path or external URL
client = SRGClient(api_key="srgplus_your_key")
profile = client.hub_profiles.update(
    "01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy (Updated)",
    user_name="acme-academy",
    cover_image="/path/to/new_cover.png",
)
# profile is GetHubProfile with cover already populated
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy (Updated)",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-academy.png",
            extension="png",
        ),
        modified="2025-06-01T12:00:00Z",
    ),
    buttons=[],
    widgets=[],
)
```

<a id="srg.resources.hub_profiles.HubProfilesResource.archive"></a>

#### archive

```python
def archive(hub_profile_id: str) -> None
```

Archive a hub profile.

Moves the hub profile to an archived state. Archived profiles are
hidden from public listings but can be restored. Content within the
profile is preserved.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to archive.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.archive("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.HubProfilesResource.restore"></a>

#### restore

```python
def restore(hub_profile_id: str) -> None
```

Restore a previously archived hub profile.

Makes the hub profile active again after it was archived. The profile
will reappear in public listings according to its visibility setting.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to restore.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.restore("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.HubProfilesResource.delete"></a>

#### delete

```python
def delete(hub_profile_id: str) -> None
```

Permanently delete a hub profile.

Removes the hub profile and all of its data. This action is
irreversible.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.delete("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.HubProfilesResource.join"></a>

#### join

```python
def join(hub_profile_id: str) -> None
```

Join a public hub profile as the current user.

Registers the current API key user as a member of the hub profile.
Only applicable to profiles with ``availability_level == "Public"``.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to join.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.join("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.HubProfilesResource.filter"></a>

#### filter

```python
def filter(
    *,
    ids: builtins.list[str],
    availability_level: AvailabilityLevel | None = None
) -> builtins.list[HubProfileFilter]
```

Get minimal info for a list of hub profile IDs.

Batch-fetches lightweight hub profile data (ID, name, username,
avatar) for a list of known IDs. Optionally filter to a specific
visibility level.

**Arguments**:

- `ids` - List of hub profile IDs to look up.
- `availability_level` - If provided, only returns profiles matching
  this visibility level (``"Public"`` or ``"Private"``).
  

**Returns**:

  List of HubProfileFilter objects (minimal representation).
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
profiles = client.hub_profiles.filter(
    ids=[
        "01965f7a-0000-7000-8000-000000000002",
        "01965f7a-0000-7000-8000-000000000009",
    ]
)
```
  
  Example response:
```python
[
    HubProfileFilter(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        avatar=HubProfileAvatar(
            path="avatars/acme-academy.jpg",
            modified="2025-06-01T10:00:00Z",
        ),
    ),
    HubProfileFilter(
        id="01965f7a-0000-7000-8000-000000000009",
        name="Beta Hub",
        user_name="beta-hub",
        avatar=None,
    ),
]
```
<a id="srg.resources.hub_profiles.HubProfilesResource.move_to_workspace"></a>

#### move\_to\_workspace

```python
def move_to_workspace(hub_profile_id: str, workspace_id: str) -> None
```

Move a hub profile to a different workspace.

Transfers ownership of the hub profile to the specified workspace.
All existing content, channels, and permissions are preserved.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to move.
- `workspace_id` - ID of the destination workspace.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.move_to_workspace(
    "01965f7a-0000-7000-8000-000000000002",
    "01965f7a-0000-7000-8000-000000000050",
)
```
<a id="srg.resources.hub_profiles.HubProfilesResource.turn_on_community"></a>

#### turn\_on\_community

```python
def turn_on_community(hub_profile_id: str) -> None
```

Enable community features for a hub profile.

Activates the community module, which allows members to interact
with each other through posts, comments, and reactions within the
hub profile.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to enable community for.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.hub_profiles.turn_on_community("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource"></a>

## AsyncHubProfilesResource Objects

```python
class AsyncHubProfilesResource()
```

<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.create"></a>

#### create

```python
async def create(
    *,
    name: str,
    user_name: str,
    sub_name: str | None = None,
    description: str | None = None,
    primary_url: str | None = None,
    availability_level: AvailabilityLevel = "Public",
    app_clip_on: bool = False,
    buttons: list[ActionButtonUpsert] | None = None,
    avatar_image: str | Path | None = None,
    cover_image: str | Path | None = None,
    avatar_extension: str | None = None,
    cover_extension: str | None = None,
    workspace_id: str | None = None,
    widgets: list[dict] | None = None
) -> GetHubProfile | HubProfileSignedUrls
```

Create a new hub profile.

Creates a hub profile inside the workspace.

**Auto-upload mode** — pass ``avatar_image`` and/or ``cover_image`` as
a local file path or an ``http(s)://`` URL. The SDK will obtain signed
upload URLs from the API, upload the images to S3, then fetch and
return the fully populated :class:`~srg.schemas.hub_profile.GetHubProfile`
(with ``avatar``/``cover`` already set).

**Manual mode** — pass ``avatar_extension`` and/or ``cover_extension``
instead. The API returns
:class:`~srg.schemas.hub_profile.HubProfileSignedUrls` containing the
signed URLs so you can upload the images yourself.

**Arguments**:

- `name` - Display name for the hub profile.
- `user_name` - Unique username / URL slug for the hub profile.
- `sub_name` - Optional subtitle shown below the name.
- `description` - Optional text description.
- `primary_url` - Optional external URL shown on the profile.
- `availability_level` - Visibility — ``"Public"`` (default) or
  ``"Private"``.
- `app_clip_on` - Whether to enable iOS App Clip. Defaults to False.
- `buttons` - List of action buttons to display on the profile page.
- `avatar_image` - Local path or ``http(s)://`` URL of the avatar image.
  The extension is derived automatically. Triggers auto-upload.
- `cover_image` - Local path or ``http(s)://`` URL of the cover image.
  The extension is derived automatically. Triggers auto-upload.
- `avatar_extension` - File extension for the avatar image (e.g.
  ``"jpg"``). Used in manual mode when ``avatar_image`` is not
  provided.
- `cover_extension` - File extension for the cover image. Used in manual
  mode when ``cover_image`` is not provided.
- `workspace_id` - Workspace to create the profile in. Uses the client's
  default workspace if omitted.
- `widgets` - Profile widget configuration objects.
  

**Returns**:

  :class:`~srg.schemas.hub_profile.GetHubProfile` when
  ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
  :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
  (manual mode).
  

**Example**:

```python
# Auto-upload — pass a local path or external URL
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profile = await client.hub_profiles.create(
        name="Acme Academy",
        user_name="acme-academy",
        avatar_image="/path/to/avatar.jpg",
        cover_image="https://example.com/cover.png",
    )
# profile is GetHubProfile with avatar and cover already populated
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    avatar=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/avatars/acme-academy.jpg",
            extension="jpg",
        ),
        modified="2025-06-01T10:00:00Z",
    ),
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-academy.png",
            extension="png",
        ),
        modified="2025-06-01T10:00:00Z",
    ),
    buttons=[],
    widgets=[],
)
```

<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.get"></a>

#### get

```python
async def get(hub_profile_id: str) -> GetHubProfile
```

Get a hub profile by ID.

Retrieves the full details of a hub profile, including its name,
username, description, avatar, cover, action buttons, and widgets.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to retrieve.
  

**Returns**:

  GetHubProfile with all profile fields.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profile = await client.hub_profiles.get(
        "01965f7a-0000-7000-8000-000000000002"
    )
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    drive_id=None,
    sub_name=None,
    description="Official learning hub for Acme Corp employees.",
    primary_url=None,
    app_clip_on=False,
    availability_level=0,
    avatar=None,
    cover=None,
    qr_code=None,
    buttons=[],
    widgets=[],
)
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.get_by_username"></a>

#### get\_by\_username

```python
async def get_by_username(username: str) -> GetHubProfile
```

Get a hub profile by its username.

Retrieves the full details of a hub profile using its URL slug
instead of its ID.

**Arguments**:

- `username` - The hub profile's username / URL slug.
  

**Returns**:

  GetHubProfile with all profile fields.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profile = await client.hub_profiles.get_by_username("acme-academy")
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    drive_id=None,
    sub_name=None,
    description="Official learning hub for Acme Corp employees.",
    primary_url=None,
    app_clip_on=False,
    availability_level=0,
    avatar=None,
    cover=None,
    qr_code=None,
    buttons=[],
    widgets=[],
)
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.list"></a>

#### list

```python
async def list() -> builtins.list[MinimalHubProfile]
```

List all hub profiles in the current workspace.

Returns a minimal summary of each hub profile in the workspace
associated with the client's API key.

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profiles = await client.hub_profiles.list()
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=None,
    ),
]
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.list_managed"></a>

#### list\_managed

```python
async def list_managed() -> builtins.list[MinimalHubProfile]
```

List all hub profiles managed by the current user.

Returns every hub profile for which the current API key user has
an Admin or Editor role.

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    managed = await client.hub_profiles.list_managed()
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=None,
    ),
]
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.update"></a>

#### update

```python
async def update(
    hub_profile_id: str,
    *,
    name: str,
    user_name: str,
    sub_name: str | None = None,
    description: str | None = None,
    primary_url: str | None = None,
    availability_level: AvailabilityLevel = "Public",
    app_clip_on: bool = False,
    buttons: builtins.list[ActionButtonUpsert] | None = None,
    avatar_image: str | Path | None = None,
    cover_image: str | Path | None = None,
    avatar: FileUploadParameters | None = None,
    cover: FileUploadParameters | None = None,
    widgets: builtins.list[dict] | None = None
) -> GetHubProfile | HubProfileSignedUrls
```

Update a hub profile's metadata and images.

Replaces the hub profile's fields with the provided values. All fields
are overwritten.

**Auto-upload mode** — pass ``avatar_image`` and/or ``cover_image`` as
a local file path or an ``http(s)://`` URL. The SDK derives the
extension, requests signed URLs, uploads the images, and returns the
updated :class:`~srg.schemas.hub_profile.GetHubProfile`.

**Manual mode** — pass ``avatar`` and/or ``cover`` as
:class:`~srg.schemas.common.FileUploadParameters`. The API returns
:class:`~srg.schemas.hub_profile.HubProfileSignedUrls` with the signed
URLs so you can upload the images yourself.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to update.
- `name` - New display name.
- `user_name` - New username / URL slug.
- `sub_name` - New subtitle. Pass ``None`` to clear.
- `description` - New description text. Pass ``None`` to clear.
- `primary_url` - New primary external URL. Pass ``None`` to clear.
- `availability_level` - New visibility — ``"Public"`` or ``"Private"``.
- `app_clip_on` - Whether to enable iOS App Clip.
- `buttons` - New list of action buttons. Replaces the existing list.
- `avatar_image` - Local path or ``http(s)://`` URL of the new avatar
  image. Triggers auto-upload.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `avatar` - Avatar upload parameters (manual mode).
- `cover` - Cover upload parameters (manual mode).
- `widgets` - New widget configuration. Replaces the existing widgets.
  

**Returns**:

  :class:`~srg.schemas.hub_profile.GetHubProfile` when
  ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
  :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
  (manual mode).
  

**Example**:

```python
# Auto-upload — pass a local path or external URL
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profile = await client.hub_profiles.update(
        "01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy (Updated)",
        user_name="acme-academy",
        cover_image="/path/to/new_cover.png",
    )
# profile is GetHubProfile with cover already populated
```
  
  Example response:
```python
GetHubProfile(
    id="01965f7a-0000-7000-8000-000000000002",
    name="Acme Academy (Updated)",
    user_name="acme-academy",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-academy.png",
            extension="png",
        ),
        modified="2025-06-01T12:00:00Z",
    ),
    buttons=[],
    widgets=[],
)
```

<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.archive"></a>

#### archive

```python
async def archive(hub_profile_id: str) -> None
```

Archive a hub profile.

Moves the hub profile to an archived state. Archived profiles are
hidden from public listings but can be restored. Content within the
profile is preserved.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to archive.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.archive("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.restore"></a>

#### restore

```python
async def restore(hub_profile_id: str) -> None
```

Restore a previously archived hub profile.

Makes the hub profile active again after it was archived.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to restore.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.restore("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.delete"></a>

#### delete

```python
async def delete(hub_profile_id: str) -> None
```

Permanently delete a hub profile.

Removes the hub profile and all of its data. This action is
irreversible.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.delete("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.join"></a>

#### join

```python
async def join(hub_profile_id: str) -> None
```

Join a public hub profile as the current user.

Registers the current API key user as a member of the hub profile.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to join.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.join("01965f7a-0000-7000-8000-000000000002")
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.filter"></a>

#### filter

```python
async def filter(
    *,
    ids: builtins.list[str],
    availability_level: AvailabilityLevel | None = None
) -> builtins.list[HubProfileFilter]
```

Get minimal info for a list of hub profile IDs.

Batch-fetches lightweight hub profile data (ID, name, username,
avatar) for a list of known IDs. Optionally filter to a specific
visibility level.

**Arguments**:

- `ids` - List of hub profile IDs to look up.
- `availability_level` - If provided, only returns profiles matching
  this visibility level (``"Public"`` or ``"Private"``).
  

**Returns**:

  List of HubProfileFilter objects (minimal representation).
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profiles = await client.hub_profiles.filter(
        ids=[
            "01965f7a-0000-7000-8000-000000000002",
            "01965f7a-0000-7000-8000-000000000009",
        ]
    )
```
  
  Example response:
```python
[
    HubProfileFilter(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Acme Academy",
        user_name="acme-academy",
        avatar=HubProfileAvatar(
            path="avatars/acme-academy.jpg",
            modified="2025-06-01T10:00:00Z",
        ),
    ),
]
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.move_to_workspace"></a>

#### move\_to\_workspace

```python
async def move_to_workspace(hub_profile_id: str, workspace_id: str) -> None
```

Move a hub profile to a different workspace.

Transfers ownership of the hub profile to the specified workspace.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to move.
- `workspace_id` - ID of the destination workspace.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.move_to_workspace(
        "01965f7a-0000-7000-8000-000000000002",
        "01965f7a-0000-7000-8000-000000000050",
    )
```
<a id="srg.resources.hub_profiles.AsyncHubProfilesResource.turn_on_community"></a>

#### turn\_on\_community

```python
async def turn_on_community(hub_profile_id: str) -> None
```

Enable community features for a hub profile.

Activates the community module for the hub profile, allowing members
to interact through posts, comments, and reactions.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to enable community for.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.hub_profiles.turn_on_community(
        "01965f7a-0000-7000-8000-000000000002"
    )
```