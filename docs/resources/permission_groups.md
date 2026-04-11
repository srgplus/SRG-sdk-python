<a id="srg.resources.permission_groups"></a>

# srg.resources.permission\_groups

<a id="srg.resources.permission_groups.PermissionGroupsResource"></a>

## PermissionGroupsResource Objects

```python
class PermissionGroupsResource()
```

<a id="srg.resources.permission_groups.PermissionGroupsResource.create"></a>

#### create

```python
def create(
    target_type: str,
    target_id: str,
    *,
    name: str
) -> str
```

Create a new permission group on a target.

Permission groups allow you to batch-assign roles to multiple users
on a hub profile or workspace. Once created, users can be added to
the group and will inherit its permissions.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `name` - Display name for the new permission group.
  

**Returns**:

  ID of the newly created permission group.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
group_id = client.permission_groups.create(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
    name="Content Editors",
)
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000030"
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.list"></a>

#### list

```python
def list(target_type: str, target_id: str) -> list[PermissionGroup]
```

List all permission groups for a target.

Returns all permission groups defined on the given hub profile or
workspace, along with their member counts.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
  

**Returns**:

  List of PermissionGroup objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
groups = client.permission_groups.list(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
)
```
  
  Example response:
```python
[
    PermissionGroup(
        id="01965f7a-0000-7000-8000-000000000030",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        name="Content Editors",
        total_users=3,
    ),
    PermissionGroup(
        id="01965f7a-0000-7000-8000-000000000031",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        name="Viewers",
        total_users=10,
    ),
]
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.get"></a>

#### get

```python
def get(group_id: str) -> GetPermissionGroup
```

Get a permission group by ID, including its members.

Retrieves the full details of a permission group and the list of
users currently in the group.

**Arguments**:

- `group_id` - ID of the permission group.
  

**Returns**:

  GetPermissionGroup containing the group metadata and its members.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
group = client.permission_groups.get("01965f7a-0000-7000-8000-000000000030")
```
  
  Example response:
```python
GetPermissionGroup(
    permission_group=PermissionGroup(
        id="01965f7a-0000-7000-8000-000000000030",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        name="Content Editors",
        total_users=2,
    ),
    users=[
        PermissionGroupUser(
            id="01965f7a-0000-7000-8000-000000000007",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
        ),
        PermissionGroupUser(
            id="01965f7a-0000-7000-8000-000000000008",
            email="jane.doe@example.com",
            first_name="Jane",
            last_name="Doe",
        ),
    ],
)
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.update"></a>

#### update

```python
def update(group_id: str, *, name: str) -> None
```

Update the name of a permission group.

Renames the permission group. Does not affect the group's members
or their permissions.

**Arguments**:

- `group_id` - ID of the permission group.
- `name` - New display name for the group.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permission_groups.update(
    "01965f7a-0000-7000-8000-000000000030",
    name="Senior Editors",
)
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.delete"></a>

#### delete

```python
def delete(group_id: str) -> None
```

Delete a permission group.

Permanently removes the permission group. Users who were members of
the group will lose any permissions they inherited from it.

**Arguments**:

- `group_id` - ID of the permission group to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permission_groups.delete("01965f7a-0000-7000-8000-000000000030")
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.add_users"></a>

#### add\_users

```python
def add_users(group_id: str, *, user_ids: builtins.list[str]) -> None
```

Add users to a permission group.

Adds one or more users to the group. They will immediately inherit
the group's permissions on the associated target.

**Arguments**:

- `group_id` - ID of the permission group.
- `user_ids` - List of user IDs to add to the group.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permission_groups.add_users(
    "01965f7a-0000-7000-8000-000000000030",
    user_ids=[
        "01965f7a-0000-7000-8000-000000000007",
        "01965f7a-0000-7000-8000-000000000008",
    ],
)
```
<a id="srg.resources.permission_groups.PermissionGroupsResource.remove_user"></a>

#### remove\_user

```python
def remove_user(group_id: str, user_id: str) -> None
```

Remove a user from a permission group.

Removes the user from the group. They will immediately lose the
permissions they inherited from it on the associated target.

**Arguments**:

- `group_id` - ID of the permission group.
- `user_id` - ID of the user to remove.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.permission_groups.remove_user(
    "01965f7a-0000-7000-8000-000000000030",
    "01965f7a-0000-7000-8000-000000000007",
)
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource"></a>

## AsyncPermissionGroupsResource Objects

```python
class AsyncPermissionGroupsResource()
```

<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.create"></a>

#### create

```python
async def create(
    target_type: str,
    target_id: str,
    *,
    name: str
) -> str
```

Create a new permission group on a target.

Permission groups allow you to batch-assign roles to multiple users
on a hub profile or workspace. Once created, users can be added to
the group and will inherit its permissions.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `name` - Display name for the new permission group.
  

**Returns**:

  ID of the newly created permission group.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    group_id = await client.permission_groups.create(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
        name="Content Editors",
    )
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000030"
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.list"></a>

#### list

```python
async def list(target_type: str, target_id: str) -> list[PermissionGroup]
```

List all permission groups for a target.

Returns all permission groups defined on the given hub profile or
workspace, along with their member counts.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
  

**Returns**:

  List of PermissionGroup objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    groups = await client.permission_groups.list(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
    )
```
  
  Example response:
```python
[
    PermissionGroup(
        id="01965f7a-0000-7000-8000-000000000030",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        name="Content Editors",
        total_users=3,
    ),
]
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.get"></a>

#### get

```python
async def get(group_id: str) -> GetPermissionGroup
```

Get a permission group by ID, including its members.

Retrieves the full details of a permission group and the list of
users currently in the group.

**Arguments**:

- `group_id` - ID of the permission group.
  

**Returns**:

  GetPermissionGroup containing the group metadata and its members.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    group = await client.permission_groups.get(
        "01965f7a-0000-7000-8000-000000000030"
    )
```
  
  Example response:
```python
GetPermissionGroup(
    permission_group=PermissionGroup(
        id="01965f7a-0000-7000-8000-000000000030",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        name="Content Editors",
        total_users=2,
    ),
    users=[
        PermissionGroupUser(
            id="01965f7a-0000-7000-8000-000000000007",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
        ),
    ],
)
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.update"></a>

#### update

```python
async def update(group_id: str, *, name: str) -> None
```

Update the name of a permission group.

Renames the permission group. Does not affect the group's members
or their permissions.

**Arguments**:

- `group_id` - ID of the permission group.
- `name` - New display name for the group.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permission_groups.update(
        "01965f7a-0000-7000-8000-000000000030",
        name="Senior Editors",
    )
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.delete"></a>

#### delete

```python
async def delete(group_id: str) -> None
```

Delete a permission group.

Permanently removes the permission group. Users who were members of
the group will lose any permissions they inherited from it.

**Arguments**:

- `group_id` - ID of the permission group to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permission_groups.delete(
        "01965f7a-0000-7000-8000-000000000030"
    )
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.add_users"></a>

#### add\_users

```python
async def add_users(group_id: str, *, user_ids: builtins.list[str]) -> None
```

Add users to a permission group.

Adds one or more users to the group. They will immediately inherit
the group's permissions on the associated target.

**Arguments**:

- `group_id` - ID of the permission group.
- `user_ids` - List of user IDs to add to the group.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permission_groups.add_users(
        "01965f7a-0000-7000-8000-000000000030",
        user_ids=[
            "01965f7a-0000-7000-8000-000000000007",
            "01965f7a-0000-7000-8000-000000000008",
        ],
    )
```
<a id="srg.resources.permission_groups.AsyncPermissionGroupsResource.remove_user"></a>

#### remove\_user

```python
async def remove_user(group_id: str, user_id: str) -> None
```

Remove a user from a permission group.

Removes the user from the group. They will immediately lose the
permissions they inherited from it on the associated target.

**Arguments**:

- `group_id` - ID of the permission group.
- `user_id` - ID of the user to remove.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.permission_groups.remove_user(
        "01965f7a-0000-7000-8000-000000000030",
        "01965f7a-0000-7000-8000-000000000007",
    )
```