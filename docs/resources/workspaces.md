<a id="srg.resources.workspaces"></a>

# srg.resources.workspaces

<a id="srg.resources.workspaces.WorkspacesResource"></a>

## WorkspacesResource Objects

```python
class WorkspacesResource()
```

<a id="srg.resources.workspaces.WorkspacesResource.get"></a>

#### get

```python
def get(workspace_id: str) -> Workspace
```

Get a workspace by ID.

Retrieves full workspace details, including its name, cover image,
seat usage, subscription plan, and the list of hub profiles it contains.

**Arguments**:

- `workspace_id` - ID of the workspace to retrieve.
  

**Returns**:

  Workspace object with subscription and hub profile details.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
workspace = client.workspaces.get("01965f7a-0000-7000-8000-000000000001")
```
  
  Example response:
```python
Workspace(
    id="01965f7a-0000-7000-8000-000000000001",
    name="Acme Corp",
    cover=None,
    memory_usage=52428800,
    seats=[
        Seat(name="Creator", users_count=2, limit=5),
    ],
    subscription_details=SubscriptionDetails(
        subscription_plan="Pro",
        customer_portal_url="https://billing.stripe.com/portal/abc",
        billing_data=SubscriptionBillingData(
            next_billing_date="2025-07-01",
            amount=99.0,
            currency="USD",
        ),
    ),
    hub_profiles=[
        WorkspaceHubProfile(
            id="01965f7a-0000-7000-8000-000000000002",
            name="Main Profile",
            user_name="main-profile",
            avatar=None,
        ),
    ],
)
```
<a id="srg.resources.workspaces.WorkspacesResource.update"></a>

#### update

```python
def update(
    workspace_id: str,
    *,
    name: str,
    cover_image: str | Path | None = None,
    cover: FileUploadParameters | None = None
) -> Workspace | WorkspaceSignedUrl
```

Update the workspace's name and cover image.

**Auto-upload mode** — pass ``cover_image`` as a local file path or an
``http(s)://`` URL. The SDK uploads the image and returns the updated
:class:`~srg.schemas.workspace.Workspace`.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.FileUploadParameters`. The API returns
:class:`~srg.schemas.workspace.WorkspaceSignedUrl` with a signed URL
so you can upload the image yourself.

**Arguments**:

- `workspace_id` - ID of the workspace to update.
- `name` - New display name for the workspace.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
  

**Returns**:

  :class:`~srg.schemas.workspace.Workspace` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.workspace.WorkspaceSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
workspace = client.workspaces.update(
    "01965f7a-0000-7000-8000-000000000001",
    name="Acme Corp (New)",
    cover_image="/path/to/cover.jpg",
)
# workspace is Workspace with cover already populated
```
  
  Example response:
```python
Workspace(
    id="01965f7a-0000-7000-8000-000000000001",
    name="Acme Corp (New)",
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-corp.jpg",
            extension="jpg",
        ),
        modified="2025-06-01T12:00:00Z",
    ),
    memory_usage=52428800,
    seats=[Seat(name="Creator", users_count=2, limit=5)],
    subscription_details=None,
    hub_profiles=[],
)
```

<a id="srg.resources.workspaces.WorkspacesResource.get_hub_profiles"></a>

#### get\_hub\_profiles

```python
def get_hub_profiles(workspace_id: str) -> list[MinimalHubProfile]
```

Get all hub profiles in a workspace.

Returns a minimal representation of each hub profile that belongs to the
given workspace. Use ``hub_profiles.get(id)`` to fetch full details for
a specific profile.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
profiles = client.workspaces.get_hub_profiles(
    "01965f7a-0000-7000-8000-000000000001"
)
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Main Profile",
        user_name="main-profile",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=None,
    ),
]
```
<a id="srg.resources.workspaces.WorkspacesResource.create_action"></a>

#### create\_action

```python
def create_action(
    workspace_id: str,
    *,
    title: str,
    metadata: Any,
    hub_profile_ids: list[str] | None = None,
    details: str | None = None
) -> str
```

Create an automation action for a workspace.

Actions are triggered automatically by platform events such as a user
completing content. The ``metadata`` object defines the action type and
its configuration (e.g. a webhook URL for
``ProgressionUpdatedMetadata``).

**Arguments**:

- `workspace_id` - ID of the workspace to attach the action to.
- `title` - Display title for the action.
- `metadata` - Action metadata object (e.g. ``ProgressionUpdatedMetadata``).
  Must be a Pydantic model or a plain dict matching the backend schema.
- `hub_profile_ids` - IDs of hub profiles to associate the action with.
  The action will fire for events on these profiles. Defaults to all.
- `details` - Optional description of what the action does.
  

**Returns**:

  ID of the newly created action.
  

**Example**:

```python
from sdk.schemas.workspace import ProgressionUpdatedMetadata

client = SRGClient(api_key="srgplus_your_key")
action_id = client.workspaces.create_action(
    "01965f7a-0000-7000-8000-000000000001",
    title="Notify on completion",
    metadata=ProgressionUpdatedMetadata(
        webhook_url="https://hooks.example.com/srg"
    ),
    hub_profile_ids=["01965f7a-0000-7000-8000-000000000002"],
    details="Fires when a user completes any content item.",
)
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000040"
```
<a id="srg.resources.workspaces.WorkspacesResource.list_actions"></a>

#### list\_actions

```python
def list_actions(workspace_id: str) -> list[MinimalAction]
```

List all automation actions for a workspace.

Returns a minimal summary of every action configured on the workspace.
Use ``get_action`` to retrieve full details including hub profile
associations and metadata.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of MinimalAction objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
actions = client.workspaces.list_actions("01965f7a-0000-7000-8000-000000000001")
```
  
  Example response:
```python
[
    MinimalAction(
        id="01965f7a-0000-7000-8000-000000000040",
        title="Notify on completion",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        details="Fires when a user completes any content item.",
    ),
]
```
<a id="srg.resources.workspaces.WorkspacesResource.get_action"></a>

#### get\_action

```python
def get_action(workspace_id: str, action_id: str) -> Action
```

Get an automation action by ID.

Retrieves the full details of an action, including its metadata and
the list of associated hub profiles.

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to retrieve.
  

**Returns**:

  Action object with metadata and hub profile associations.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
action = client.workspaces.get_action(
    "01965f7a-0000-7000-8000-000000000001",
    "01965f7a-0000-7000-8000-000000000040",
)
```
  
  Example response:
```python
Action(
    id="01965f7a-0000-7000-8000-000000000040",
    title="Notify on completion",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    details="Fires when a user completes any content item.",
    action_metadata=ActionMetadata(
        dollar_type="ProgressionUpdatedMetadata",
        webhook_url="https://hooks.example.com/srg",
    ),
    hub_profiles=[
        MinimalHubProfile(
            id="01965f7a-0000-7000-8000-000000000002",
            name="Main Profile",
            user_name="main-profile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
            drive_id=None,
            avatar=None,
        ),
    ],
)
```
<a id="srg.resources.workspaces.WorkspacesResource.update_action"></a>

#### update\_action

```python
def update_action(
    workspace_id: str,
    action_id: str,
    *,
    title: str,
    metadata: Any,
    hub_profile_ids: list[str] | None = None,
    details: str | None = None
) -> None
```

Update an automation action.

Replaces the action's title, metadata, hub profile associations, and
optional description. All fields are overwritten (not patched).

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to update.
- `title` - New display title.
- `metadata` - New metadata object (e.g. ``ProgressionUpdatedMetadata``).
- `hub_profile_ids` - New list of hub profile IDs to associate with.
  Replaces the existing list.
- `details` - New description. Omit to clear the current description.
  

**Example**:

```python
from sdk.schemas.workspace import ProgressionUpdatedMetadata

client = SRGClient(api_key="srgplus_your_key")
client.workspaces.update_action(
    "01965f7a-0000-7000-8000-000000000001",
    "01965f7a-0000-7000-8000-000000000040",
    title="Notify on completion (updated)",
    metadata=ProgressionUpdatedMetadata(
        webhook_url="https://hooks.example.com/srg-v2"
    ),
    hub_profile_ids=["01965f7a-0000-7000-8000-000000000002"],
)
```
<a id="srg.resources.workspaces.WorkspacesResource.delete_action"></a>

#### delete\_action

```python
def delete_action(workspace_id: str, action_id: str) -> None
```

Delete an automation action.

Permanently removes the action from the workspace. Any future events
that would have triggered it will no longer fire the webhook.

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.workspaces.delete_action(
    "01965f7a-0000-7000-8000-000000000001",
    "01965f7a-0000-7000-8000-000000000040",
)
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource"></a>

## AsyncWorkspacesResource Objects

```python
class AsyncWorkspacesResource()
```

<a id="srg.resources.workspaces.AsyncWorkspacesResource.get"></a>

#### get

```python
async def get(workspace_id: str) -> Workspace
```

Get a workspace by ID.

Retrieves full workspace details, including its name, cover image,
seat usage, subscription plan, and the list of hub profiles it contains.

**Arguments**:

- `workspace_id` - ID of the workspace to retrieve.
  

**Returns**:

  Workspace object with subscription and hub profile details.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    workspace = await client.workspaces.get(
        "01965f7a-0000-7000-8000-000000000001"
    )
```
  
  Example response:
```python
Workspace(
    id="01965f7a-0000-7000-8000-000000000001",
    name="Acme Corp",
    cover=None,
    memory_usage=52428800,
    seats=[Seat(name="Creator", users_count=2, limit=5)],
    subscription_details=SubscriptionDetails(
        subscription_plan="Pro",
        customer_portal_url="https://billing.stripe.com/portal/abc",
        billing_data=SubscriptionBillingData(
            next_billing_date="2025-07-01",
            amount=99.0,
            currency="USD",
        ),
    ),
    hub_profiles=[
        WorkspaceHubProfile(
            id="01965f7a-0000-7000-8000-000000000002",
            name="Main Profile",
            user_name="main-profile",
            avatar=None,
        ),
    ],
)
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.update"></a>

#### update

```python
async def update(
    workspace_id: str,
    *,
    name: str,
    cover_image: str | Path | None = None,
    cover: FileUploadParameters | None = None
) -> Workspace | WorkspaceSignedUrl
```

Update the workspace's name and cover image.

**Auto-upload mode** — pass ``cover_image`` as a local file path or an
``http(s)://`` URL. The SDK uploads the image and returns the updated
:class:`~srg.schemas.workspace.Workspace`.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.FileUploadParameters`. The API returns
:class:`~srg.schemas.workspace.WorkspaceSignedUrl` with a signed URL
so you can upload the image yourself.

**Arguments**:

- `workspace_id` - ID of the workspace to update.
- `name` - New display name for the workspace.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
  

**Returns**:

  :class:`~srg.schemas.workspace.Workspace` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.workspace.WorkspaceSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    workspace = await client.workspaces.update(
        "01965f7a-0000-7000-8000-000000000001",
        name="Acme Corp (New)",
        cover_image="/path/to/cover.jpg",
    )
# workspace is Workspace with cover already populated
```
  
  Example response:
```python
Workspace(
    id="01965f7a-0000-7000-8000-000000000001",
    name="Acme Corp (New)",
    cover=Cover(
        details=CoverDetails(
            url="https://cdn.srgplus.com/covers/acme-corp.jpg",
            extension="jpg",
        ),
        modified="2025-06-01T12:00:00Z",
    ),
    memory_usage=52428800,
    seats=[Seat(name="Creator", users_count=2, limit=5)],
    subscription_details=None,
    hub_profiles=[],
)
```

<a id="srg.resources.workspaces.AsyncWorkspacesResource.get_hub_profiles"></a>

#### get\_hub\_profiles

```python
async def get_hub_profiles(workspace_id: str) -> list[MinimalHubProfile]
```

Get all hub profiles in a workspace.

Returns a minimal representation of each hub profile that belongs to the
given workspace. Use ``hub_profiles.get(id)`` to fetch full details for
a specific profile.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of MinimalHubProfile objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    profiles = await client.workspaces.get_hub_profiles(
        "01965f7a-0000-7000-8000-000000000001"
    )
```
  
  Example response:
```python
[
    MinimalHubProfile(
        id="01965f7a-0000-7000-8000-000000000002",
        name="Main Profile",
        user_name="main-profile",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        drive_id=None,
        avatar=None,
    ),
]
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.create_action"></a>

#### create\_action

```python
async def create_action(
    workspace_id: str,
    *,
    title: str,
    metadata: Any,
    hub_profile_ids: list[str] | None = None,
    details: str | None = None
) -> str
```

Create an automation action for a workspace.

Actions are triggered automatically by platform events such as a user
completing content. The ``metadata`` object defines the action type and
its configuration (e.g. a webhook URL for
``ProgressionUpdatedMetadata``).

**Arguments**:

- `workspace_id` - ID of the workspace to attach the action to.
- `title` - Display title for the action.
- `metadata` - Action metadata object (e.g. ``ProgressionUpdatedMetadata``).
  Must be a Pydantic model or a plain dict matching the backend schema.
- `hub_profile_ids` - IDs of hub profiles to associate the action with.
  Defaults to all.
- `details` - Optional description of what the action does.
  

**Returns**:

  ID of the newly created action.
  

**Example**:

```python
from sdk.schemas.workspace import ProgressionUpdatedMetadata

async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    action_id = await client.workspaces.create_action(
        "01965f7a-0000-7000-8000-000000000001",
        title="Notify on completion",
        metadata=ProgressionUpdatedMetadata(
            webhook_url="https://hooks.example.com/srg"
        ),
        hub_profile_ids=["01965f7a-0000-7000-8000-000000000002"],
    )
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000040"
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.list_actions"></a>

#### list\_actions

```python
async def list_actions(workspace_id: str) -> list[MinimalAction]
```

List all automation actions for a workspace.

Returns a minimal summary of every action configured on the workspace.
Use ``get_action`` to retrieve full details including hub profile
associations and metadata.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of MinimalAction objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    actions = await client.workspaces.list_actions(
        "01965f7a-0000-7000-8000-000000000001"
    )
```
  
  Example response:
```python
[
    MinimalAction(
        id="01965f7a-0000-7000-8000-000000000040",
        title="Notify on completion",
        workspace_id="01965f7a-0000-7000-8000-000000000001",
        details="Fires when a user completes any content item.",
    ),
]
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.get_action"></a>

#### get\_action

```python
async def get_action(workspace_id: str, action_id: str) -> Action
```

Get an automation action by ID.

Retrieves the full details of an action, including its metadata and
the list of associated hub profiles.

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to retrieve.
  

**Returns**:

  Action object with metadata and hub profile associations.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    action = await client.workspaces.get_action(
        "01965f7a-0000-7000-8000-000000000001",
        "01965f7a-0000-7000-8000-000000000040",
    )
```
  
  Example response:
```python
Action(
    id="01965f7a-0000-7000-8000-000000000040",
    title="Notify on completion",
    workspace_id="01965f7a-0000-7000-8000-000000000001",
    details="Fires when a user completes any content item.",
    action_metadata=ActionMetadata(
        dollar_type="ProgressionUpdatedMetadata",
        webhook_url="https://hooks.example.com/srg",
    ),
    hub_profiles=[
        MinimalHubProfile(
            id="01965f7a-0000-7000-8000-000000000002",
            name="Main Profile",
            user_name="main-profile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
            drive_id=None,
            avatar=None,
        ),
    ],
)
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.update_action"></a>

#### update\_action

```python
async def update_action(
    workspace_id: str,
    action_id: str,
    *,
    title: str,
    metadata: Any,
    hub_profile_ids: list[str] | None = None,
    details: str | None = None
) -> None
```

Update an automation action.

Replaces the action's title, metadata, hub profile associations, and
optional description. All fields are overwritten (not patched).

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to update.
- `title` - New display title.
- `metadata` - New metadata object (e.g. ``ProgressionUpdatedMetadata``).
- `hub_profile_ids` - New list of hub profile IDs. Replaces the existing list.
- `details` - New description. Omit to clear the current description.
  

**Example**:

```python
from sdk.schemas.workspace import ProgressionUpdatedMetadata

async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.workspaces.update_action(
        "01965f7a-0000-7000-8000-000000000001",
        "01965f7a-0000-7000-8000-000000000040",
        title="Notify on completion (updated)",
        metadata=ProgressionUpdatedMetadata(
            webhook_url="https://hooks.example.com/srg-v2"
        ),
    )
```
<a id="srg.resources.workspaces.AsyncWorkspacesResource.delete_action"></a>

#### delete\_action

```python
async def delete_action(workspace_id: str, action_id: str) -> None
```

Delete an automation action.

Permanently removes the action from the workspace. Any future events
that would have triggered it will no longer fire the webhook.

**Arguments**:

- `workspace_id` - ID of the workspace.
- `action_id` - ID of the action to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.workspaces.delete_action(
        "01965f7a-0000-7000-8000-000000000001",
        "01965f7a-0000-7000-8000-000000000040",
    )
```