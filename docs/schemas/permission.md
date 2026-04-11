## GetPermissionGroup

*model* `GetPermissionGroup(permission_group, users)`

**Fields**

- **permission_group** (*PermissionGroup*)
- **users** (*list[PermissionGroupUser]*)

## GetTarget

*model* `GetTarget(target_id, can_archive=False, can_manage=False, can_edit=False)`

**Fields**

- **target_id** (*str*)
- **can_archive** (*bool, optional*) – Defaults to `False`.
- **can_manage** (*bool, optional*) – Defaults to `False`.
- **can_edit** (*bool, optional*) – Defaults to `False`.

## PermissionGroup

*model* `PermissionGroup(id, target_id, target_type, total_users, name=None)`

**Fields**

- **id** (*str*)
- **target_id** (*str*)
- **target_type** (*str*)
- **total_users** (*int*)
- **name** (*str | None, optional*) – Defaults to `None`.

## PermissionGroupUser

*model* `PermissionGroupUser(id, email=None, first_name=None, last_name=None)`

**Fields**

- **id** (*str*)
- **email** (*str | None, optional*) – Defaults to `None`.
- **first_name** (*str | None, optional*) – Defaults to `None`.
- **last_name** (*str | None, optional*) – Defaults to `None`.

## WorkspaceUser

*model* `WorkspaceUser(id, hub_profile_highest_role, workspace_role=None, profile)`

**Fields**

- **id** (*str*)
- **hub_profile_highest_role** (*WorkspaceUserRole*)
- **workspace_role** (*WorkspaceUserRole | None, optional*) – Defaults to `None`.
- **profile** (*WorkspaceUserProfile*)

## WorkspaceUserProfile

*model* `WorkspaceUserProfile(email, first_name, last_name, avatar_url=None)`

**Fields**

- **email** (*str*)
- **first_name** (*str*)
- **last_name** (*str*)
- **avatar_url** (*SignedUrl | None, optional*) – Defaults to `None`.

## WorkspaceUserRole

*model* `WorkspaceUserRole(id, name)`

Role object returned as \{id, name\} from the backend Enumeration.

**Fields**

- **id** (*int*)
- **name** (*str*)
