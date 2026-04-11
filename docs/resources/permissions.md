<a id="srg.resources.permissions"></a>

# srg.resources.permissions

<a id="srg.resources.permissions.PermissionsResource"></a>

## PermissionsResource Objects

```python
class PermissionsResource()
```

<a id="srg.resources.permissions.PermissionsResource.give"></a>

#### give

```python
def give(
    *,
    user_id: str,
    target_id: str,
    target_type: str,
    role_id: int
) -> None
```

Assign a role to a user on a target.

Grants the specified user the given role on a hub profile, workspace,
channel, or other target resource. If the user already has a role on
that target it will be replaced.

**Arguments**:

- `user_id` - ID of the user to grant access to.
- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``,
  ``"Channel"``).
- `role_id` - Role ID to assign (e.g. ``1`` for Admin, ``2`` for Editor,
  ``3`` for Viewer).
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permissions.give(
    user_id="01965f7a-0000-7000-8000-000000000007",
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
    role_id=2,
)
```
<a id="srg.resources.permissions.PermissionsResource.delete"></a>

#### delete

```python
def delete(
    *,
    target_type: str,
    target_id: str,
    user_id: str
) -> None
```

Remove a user's role from a target.

Revokes all permissions the user holds on the specified target.
The user will no longer have access unless they are a member of a
permission group that grants access.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `user_id` - ID of the user whose permission to remove.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permissions.delete(
    target_type="HubProfile",
    target_id="01965f7a-0000-7000-8000-000000000002",
    user_id="01965f7a-0000-7000-8000-000000000007",
)
```
<a id="srg.resources.permissions.PermissionsResource.can_read"></a>

#### can\_read

```python
def can_read(*, target_id: str, target_type: str) -> bool
```

Check whether the current API key user can read a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Content"``).
  

**Returns**:

  True if the current user has read access to the target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
readable = client.permissions.can_read(
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
)
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.PermissionsResource.can_edit"></a>

#### can\_edit

```python
def can_edit(*, target_id: str, target_type: str) -> bool
```

Check whether the current API key user can edit a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Content"``).
  

**Returns**:

  True if the current user has edit access to the target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
editable = client.permissions.can_edit(
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
)
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.PermissionsResource.can_create_child"></a>

#### can\_create\_child

```python
def can_create_child(
    *,
    parent_target_type: str,
    parent_target_id: str,
    child_target_type: str
) -> bool
```

Check whether the current user can create a child resource inside a parent.

Useful for verifying whether the current user is allowed to, for example,
create a Channel inside a HubProfile before attempting the operation.

**Arguments**:

- `parent_target_type` - Type of the parent resource (e.g. ``"HubProfile"``).
- `parent_target_id` - ID of the parent resource.
- `child_target_type` - Type of the child resource to check (e.g.
  ``"Channel"``, ``"Content"``).
  

**Returns**:

  True if the current user can create the specified child resource.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
allowed = client.permissions.can_create_child(
    parent_target_type="HubProfile",
    parent_target_id="01965f7a-0000-7000-8000-000000000002",
    child_target_type="Channel",
)
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.PermissionsResource.can_manage_permissions"></a>

#### can\_manage\_permissions

```python
def can_manage_permissions(*, target_id: str, target_type: str) -> bool
```

Check whether the current user can manage permissions on a target.

Returns True if the current user has the right to grant or revoke
roles for other users on the specified target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
  

**Returns**:

  True if the current user can manage permissions on the target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
can_manage = client.permissions.can_manage_permissions(
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
)
```
  
  Example response:
```python
False
```
<a id="srg.resources.permissions.PermissionsResource.can_archive"></a>

#### can\_archive

```python
def can_archive(*, target_id: str, target_type: str) -> bool
```

Check whether the current user can archive a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Channel"``).
  

**Returns**:

  True if the current user can archive the target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
can_archive = client.permissions.can_archive(
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
)
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.PermissionsResource.is_member"></a>

#### is\_member

```python
def is_member(*, target_id: str, target_type: str) -> bool
```

Check whether the current user is a member of a target.

A user is considered a member if they have any role (including
Viewer) on the specified target, or belong to a permission group
associated with it.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
  

**Returns**:

  True if the current user is a member of the target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
member = client.permissions.is_member(
    target_id="01965f7a-0000-7000-8000-000000000002",
    target_type="HubProfile",
)
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.PermissionsResource.get_targets"></a>

#### get\_targets

```python
def get_targets(
    parent_target_type: str,
    *,
    child_target_type: str | None = None,
    parent_target_id: str | None = None
) -> list[GetTarget]
```

Get all targets of a given type accessible to the current user.

Returns the list of target resources of ``parent_target_type`` that the
current user can access, along with their permission flags. Optionally
filter by child type or parent ID.

**Arguments**:

- `parent_target_type` - Type of the targets to list (e.g. ``"HubProfile"``,
  ``"Workspace"``).
- `child_target_type` - If provided, filters to targets that have a child
  of this type.
- `parent_target_id` - If provided, filters to targets that belong to this
  parent.
  

**Returns**:

  List of GetTarget objects with permission flags for each target.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
targets = client.permissions.get_targets("HubProfile")
```
  
  Example response:
```python
[
    GetTarget(
        target_id="01965f7a-0000-7000-8000-000000000002",
        can_archive=True,
        can_manage=True,
        can_edit=True,
    ),
    GetTarget(
        target_id="01965f7a-0000-7000-8000-000000000009",
        can_archive=False,
        can_manage=False,
        can_edit=True,
    ),
]
```
<a id="srg.resources.permissions.PermissionsResource.get_workspace_users"></a>

#### get\_workspace\_users

```python
def get_workspace_users(workspace_id: str) -> list[WorkspaceUser]
```

Get all users with access to a workspace.

Returns every user who has a role on the workspace, along with their
profile, workspace role, and their highest role across all hub profiles
in that workspace.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of WorkspaceUser objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
users = client.permissions.get_workspace_users(
    "01965f7a-0000-7000-8000-000000000001"
)
```
  
  Example response:
```python
[
    WorkspaceUser(
        id="01965f7a-0000-7000-8000-000000000007",
        workspace_role=WorkspaceUserRole(id=1, name="Admin"),
        hub_profile_highest_role=WorkspaceUserRole(id=1, name="Admin"),
        profile=WorkspaceUserProfile(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            avatar_url=None,
        ),
    ),
]
```
<a id="srg.resources.permissions.AsyncPermissionsResource"></a>

## AsyncPermissionsResource Objects

```python
class AsyncPermissionsResource()
```

<a id="srg.resources.permissions.AsyncPermissionsResource.give"></a>

#### give

```python
async def give(
    *,
    user_id: str,
    target_id: str,
    target_type: str,
    role_id: int
) -> None
```

Assign a role to a user on a target.

Grants the specified user the given role on a hub profile, workspace,
channel, or other target resource. If the user already has a role on
that target it will be replaced.

**Arguments**:

- `user_id` - ID of the user to grant access to.
- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``,
  ``"Channel"``).
- `role_id` - Role ID to assign (e.g. ``1`` for Admin, ``2`` for Editor,
  ``3`` for Viewer).
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permissions.give(
        user_id="01965f7a-0000-7000-8000-000000000007",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        role_id=2,
    )
```
<a id="srg.resources.permissions.AsyncPermissionsResource.delete"></a>

#### delete

```python
async def delete(
    *,
    target_type: str,
    target_id: str,
    user_id: str
) -> None
```

Remove a user's role from a target.

Revokes all permissions the user holds on the specified target.
The user will no longer have access unless they are a member of a
permission group that grants access.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `user_id` - ID of the user whose permission to remove.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permissions.delete(
        target_type="HubProfile",
        target_id="01965f7a-0000-7000-8000-000000000002",
        user_id="01965f7a-0000-7000-8000-000000000007",
    )
```
<a id="srg.resources.permissions.AsyncPermissionsResource.can_read"></a>

#### can\_read

```python
async def can_read(*, target_id: str, target_type: str) -> bool
```

Check whether the current API key user can read a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Content"``).
  

**Returns**:

  True if the current user has read access to the target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    readable = await client.permissions.can_read(
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
    )
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.AsyncPermissionsResource.can_edit"></a>

#### can\_edit

```python
async def can_edit(*, target_id: str, target_type: str) -> bool
```

Check whether the current API key user can edit a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Content"``).
  

**Returns**:

  True if the current user has edit access to the target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    editable = await client.permissions.can_edit(
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
    )
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.AsyncPermissionsResource.can_create_child"></a>

#### can\_create\_child

```python
async def can_create_child(
    *,
    parent_target_type: str,
    parent_target_id: str,
    child_target_type: str
) -> bool
```

Check whether the current user can create a child resource inside a parent.

Useful for verifying whether the current user is allowed to, for example,
create a Channel inside a HubProfile before attempting the operation.

**Arguments**:

- `parent_target_type` - Type of the parent resource (e.g. ``"HubProfile"``).
- `parent_target_id` - ID of the parent resource.
- `child_target_type` - Type of the child resource to check (e.g.
  ``"Channel"``, ``"Content"``).
  

**Returns**:

  True if the current user can create the specified child resource.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    allowed = await client.permissions.can_create_child(
        parent_target_type="HubProfile",
        parent_target_id="01965f7a-0000-7000-8000-000000000002",
        child_target_type="Channel",
    )
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.AsyncPermissionsResource.can_manage_permissions"></a>

#### can\_manage\_permissions

```python
async def can_manage_permissions(*, target_id: str, target_type: str) -> bool
```

Check whether the current user can manage permissions on a target.

Returns True if the current user has the right to grant or revoke
roles for other users on the specified target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
  

**Returns**:

  True if the current user can manage permissions on the target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    can_manage = await client.permissions.can_manage_permissions(
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
    )
```
  
  Example response:
```python
False
```
<a id="srg.resources.permissions.AsyncPermissionsResource.can_archive"></a>

#### can\_archive

```python
async def can_archive(*, target_id: str, target_type: str) -> bool
```

Check whether the current user can archive a target.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Channel"``).
  

**Returns**:

  True if the current user can archive the target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    can_archive = await client.permissions.can_archive(
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
    )
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.AsyncPermissionsResource.is_member"></a>

#### is\_member

```python
async def is_member(*, target_id: str, target_type: str) -> bool
```

Check whether the current user is a member of a target.

A user is considered a member if they have any role (including
Viewer) on the specified target, or belong to a permission group
associated with it.

**Arguments**:

- `target_id` - ID of the target resource.
- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
  

**Returns**:

  True if the current user is a member of the target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    member = await client.permissions.is_member(
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
    )
```
  
  Example response:
```python
True
```
<a id="srg.resources.permissions.AsyncPermissionsResource.get_targets"></a>

#### get\_targets

```python
async def get_targets(
    parent_target_type: str,
    *,
    child_target_type: str | None = None,
    parent_target_id: str | None = None
) -> list[GetTarget]
```

Get all targets of a given type accessible to the current user.

Returns the list of target resources of ``parent_target_type`` that the
current user can access, along with their permission flags. Optionally
filter by child type or parent ID.

**Arguments**:

- `parent_target_type` - Type of the targets to list (e.g. ``"HubProfile"``,
  ``"Workspace"``).
- `child_target_type` - If provided, filters to targets that have a child
  of this type.
- `parent_target_id` - If provided, filters to targets that belong to this
  parent.
  

**Returns**:

  List of GetTarget objects with permission flags for each target.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    targets = await client.permissions.get_targets("HubProfile")
```
  
  Example response:
```python
[
    GetTarget(
        target_id="01965f7a-0000-7000-8000-000000000002",
        can_archive=True,
        can_manage=True,
        can_edit=True,
    ),
]
```
<a id="srg.resources.permissions.AsyncPermissionsResource.get_workspace_users"></a>

#### get\_workspace\_users

```python
async def get_workspace_users(workspace_id: str) -> list[WorkspaceUser]
```

Get all users with access to a workspace.

Returns every user who has a role on the workspace, along with their
profile, workspace role, and their highest role across all hub profiles
in that workspace.

**Arguments**:

- `workspace_id` - ID of the workspace.
  

**Returns**:

  List of WorkspaceUser objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    users = await client.permissions.get_workspace_users(
        "01965f7a-0000-7000-8000-000000000001"
    )
```
  
  Example response:
```python
[
    WorkspaceUser(
        id="01965f7a-0000-7000-8000-000000000007",
        workspace_role=WorkspaceUserRole(id=1, name="Admin"),
        hub_profile_highest_role=WorkspaceUserRole(id=1, name="Admin"),
        profile=WorkspaceUserProfile(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            avatar_url=None,
        ),
    ),
]
```