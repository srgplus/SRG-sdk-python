from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.exceptions import SRGError
from srg.schemas.permission import GetTarget, WorkspaceUser


class PermissionsResource:
    def __init__(self, registry: dict[str, SyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> SyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    def give(
        self,
        *,
        user_id: str,
        target_id: str,
        target_type: str,
        role_id: int,
        workspace_id: str,
    ) -> dict | None:
        """
        Assign a role to a user on a target.

        Grants the specified user the given role on a hub profile, workspace,
        channel, or other target resource. If the user already has a role on
        that target it will be replaced.

        Args:
            user_id: ID of the user to grant access to.
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``,
                ``"Channel"``).
            role_id: Role ID to assign (e.g. ``1`` for Admin, ``2`` for Editor,
                ``3`` for Viewer).

        Returns:
            The created permission record as a raw dict, or ``None`` if the
            server returns no body.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permissions.give(
            user_id="01965f7a-0000-7000-8000-000000000007",
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            role_id=2,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).post(
            "/api/v1/permissions",
            json={
                "userId": user_id,
                "targetId": target_id,
                "targetType": target_type,
                "roleId": role_id,
            },
        )

    def delete(
        self, *, target_type: str, target_id: str, user_id: str, workspace_id: str
    ) -> None:
        """
        Remove a user's role from a target.

        Revokes all permissions the user holds on the specified target.
        The user will no longer have access unless they are a member of a
        permission group that grants access.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            user_id: ID of the user whose permission to remove.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permissions.delete(
            target_type="HubProfile",
            target_id="01965f7a-0000-7000-8000-000000000002",
            user_id="01965f7a-0000-7000-8000-000000000007",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/permissions/{target_type}/{target_id}/{user_id}"
        )

    def can_read(self, *, target_id: str, target_type: str, workspace_id: str) -> bool:
        """
        Check whether the current API key user can read a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Content"``).

        Returns:
            True if the current user has read access to the target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        readable = client.permissions.can_read(
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-read/{target_type}/{target_id}"
        )
        return bool(data)

    def can_edit(self, *, target_id: str, target_type: str, workspace_id: str) -> bool:
        """
        Check whether the current API key user can edit a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Content"``).

        Returns:
            True if the current user has edit access to the target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        editable = client.permissions.can_edit(
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-edit/{target_type}/{target_id}"
        )
        return bool(data)

    def can_create_child(
        self,
        *,
        parent_target_type: str,
        parent_target_id: str,
        child_target_type: str,
        workspace_id: str,
    ) -> bool:
        """
        Check whether the current user can create a child resource inside a parent.

        Useful for verifying whether the current user is allowed to, for example,
        create a Channel inside a HubProfile before attempting the operation.

        Args:
            parent_target_type: Type of the parent resource (e.g. ``"HubProfile"``).
            parent_target_id: ID of the parent resource.
            child_target_type: Type of the child resource to check (e.g.
                ``"Channel"``, ``"Content"``).

        Returns:
            True if the current user can create the specified child resource.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        allowed = client.permissions.can_create_child(
            parent_target_type="HubProfile",
            parent_target_id="01965f7a-0000-7000-8000-000000000002",
            child_target_type="Channel",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-create-child/{parent_target_type}/{parent_target_id}/{child_target_type}"
        )
        return bool(data)

    def can_manage_permissions(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current user can manage permissions on a target.

        Returns True if the current user has the right to grant or revoke
        roles for other users on the specified target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).

        Returns:
            True if the current user can manage permissions on the target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        can_manage = client.permissions.can_manage_permissions(
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        False
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-manage-permissions/{target_type}/{target_id}"
        )
        return bool(data)

    def can_archive(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current user can archive a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Channel"``).

        Returns:
            True if the current user can archive the target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        can_archive = client.permissions.can_archive(
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-manage-archivation/{target_type}/{target_id}"
        )
        return bool(data)

    def is_member(self, *, target_id: str, target_type: str, workspace_id: str) -> bool:
        """
        Check whether the current user is a member of a target.

        A user is considered a member if they have any role (including
        Viewer) on the specified target, or belong to a permission group
        associated with it.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).

        Returns:
            True if the current user is a member of the target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        member = client.permissions.is_member(
            target_id="01965f7a-0000-7000-8000-000000000002",
            target_type="HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/is-member/{target_type}/{target_id}"
        )
        return bool(data)

    def get_targets(
        self,
        parent_target_type: str,
        *,
        child_target_type: str | None = None,
        parent_target_id: str | None = None,
        workspace_id: str,
    ) -> list[GetTarget]:
        """
        Get all targets of a given type accessible to the current user.

        Returns the list of target resources of ``parent_target_type`` that the
        current user can access, along with their permission flags. Optionally
        filter by child type or parent ID.

        Args:
            parent_target_type: Type of the targets to list (e.g. ``"HubProfile"``,
                ``"Workspace"``).
            child_target_type: If provided, filters to targets that have a child
                of this type.
            parent_target_id: If provided, filters to targets that belong to this
                parent.

        Returns:
            List of GetTarget objects with permission flags for each target.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        targets = client.permissions.get_targets(
            "HubProfile",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
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
        """
        params: dict = {}
        if child_target_type:
            params["childTargetType"] = child_target_type
        if parent_target_id:
            params["parentTargetId"] = parent_target_id
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/{parent_target_type}", params=params or None
        )
        return [GetTarget.model_validate(item) for item in (data or [])]

    def get_workspace_users(self, workspace_id: str) -> list[WorkspaceUser]:
        """
        Get all users with access to a workspace.

        Returns every user who has a role on the workspace, along with their
        profile, workspace role, and their highest role across all hub profiles
        in that workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            List of WorkspaceUser objects.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
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
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permissions/workspaces/{workspace_id}/users"
        )
        return [WorkspaceUser.model_validate(item) for item in (data or [])]


class AsyncPermissionsResource:
    def __init__(self, registry: dict[str, AsyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> AsyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    async def give(
        self,
        *,
        user_id: str,
        target_id: str,
        target_type: str,
        role_id: int,
        workspace_id: str,
    ) -> dict | None:
        """
        Assign a role to a user on a target.

        Grants the specified user the given role on a hub profile, workspace,
        channel, or other target resource. If the user already has a role on
        that target it will be replaced.

        Args:
            user_id: ID of the user to grant access to.
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``,
                ``"Channel"``).
            role_id: Role ID to assign (e.g. ``1`` for Admin, ``2`` for Editor,
                ``3`` for Viewer).

        Returns:
            The created permission record as a raw dict, or ``None`` if the
            server returns no body.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permissions.give(
                user_id="01965f7a-0000-7000-8000-000000000007",
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                role_id=2,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).post(
            "/api/v1/permissions",
            json={
                "userId": user_id,
                "targetId": target_id,
                "targetType": target_type,
                "roleId": role_id,
            },
        )

    async def delete(
        self, *, target_type: str, target_id: str, user_id: str, workspace_id: str
    ) -> None:
        """
        Remove a user's role from a target.

        Revokes all permissions the user holds on the specified target.
        The user will no longer have access unless they are a member of a
        permission group that grants access.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            user_id: ID of the user whose permission to remove.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permissions.delete(
                target_type="HubProfile",
                target_id="01965f7a-0000-7000-8000-000000000002",
                user_id="01965f7a-0000-7000-8000-000000000007",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/permissions/{target_type}/{target_id}/{user_id}"
        )

    async def can_read(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current API key user can read a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Content"``).

        Returns:
            True if the current user has read access to the target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            readable = await client.permissions.can_read(
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-read/{target_type}/{target_id}"
        )
        return bool(data)

    async def can_edit(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current API key user can edit a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Content"``).

        Returns:
            True if the current user has edit access to the target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            editable = await client.permissions.can_edit(
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-edit/{target_type}/{target_id}"
        )
        return bool(data)

    async def can_create_child(
        self,
        *,
        parent_target_type: str,
        parent_target_id: str,
        child_target_type: str,
        workspace_id: str,
    ) -> bool:
        """
        Check whether the current user can create a child resource inside a parent.

        Useful for verifying whether the current user is allowed to, for example,
        create a Channel inside a HubProfile before attempting the operation.

        Args:
            parent_target_type: Type of the parent resource (e.g. ``"HubProfile"``).
            parent_target_id: ID of the parent resource.
            child_target_type: Type of the child resource to check (e.g.
                ``"Channel"``, ``"Content"``).

        Returns:
            True if the current user can create the specified child resource.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            allowed = await client.permissions.can_create_child(
                parent_target_type="HubProfile",
                parent_target_id="01965f7a-0000-7000-8000-000000000002",
                child_target_type="Channel",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-create-child/{parent_target_type}/{parent_target_id}/{child_target_type}"
        )
        return bool(data)

    async def can_manage_permissions(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current user can manage permissions on a target.

        Returns True if the current user has the right to grant or revoke
        roles for other users on the specified target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).

        Returns:
            True if the current user can manage permissions on the target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            can_manage = await client.permissions.can_manage_permissions(
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        False
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-manage-permissions/{target_type}/{target_id}"
        )
        return bool(data)

    async def can_archive(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current user can archive a target.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Channel"``).

        Returns:
            True if the current user can archive the target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            can_archive = await client.permissions.can_archive(
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/can-manage-archivation/{target_type}/{target_id}"
        )
        return bool(data)

    async def is_member(
        self, *, target_id: str, target_type: str, workspace_id: str
    ) -> bool:
        """
        Check whether the current user is a member of a target.

        A user is considered a member if they have any role (including
        Viewer) on the specified target, or belong to a permission group
        associated with it.

        Args:
            target_id: ID of the target resource.
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).

        Returns:
            True if the current user is a member of the target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            member = await client.permissions.is_member(
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/is-member/{target_type}/{target_id}"
        )
        return bool(data)

    async def get_targets(
        self,
        parent_target_type: str,
        *,
        child_target_type: str | None = None,
        parent_target_id: str | None = None,
        workspace_id: str,
    ) -> list[GetTarget]:
        """
        Get all targets of a given type accessible to the current user.

        Returns the list of target resources of ``parent_target_type`` that the
        current user can access, along with their permission flags. Optionally
        filter by child type or parent ID.

        Args:
            parent_target_type: Type of the targets to list (e.g. ``"HubProfile"``,
                ``"Workspace"``).
            child_target_type: If provided, filters to targets that have a child
                of this type.
            parent_target_id: If provided, filters to targets that belong to this
                parent.

        Returns:
            List of GetTarget objects with permission flags for each target.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            targets = await client.permissions.get_targets(
                "HubProfile",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
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
        """
        params: dict = {}
        if child_target_type:
            params["childTargetType"] = child_target_type
        if parent_target_id:
            params["parentTargetId"] = parent_target_id
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/{parent_target_type}", params=params or None
        )
        return [GetTarget.model_validate(item) for item in (data or [])]

    async def get_workspace_users(self, workspace_id: str) -> list[WorkspaceUser]:
        """
        Get all users with access to a workspace.

        Returns every user who has a role on the workspace, along with their
        profile, workspace role, and their highest role across all hub profiles
        in that workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            List of WorkspaceUser objects.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
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
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permissions/workspaces/{workspace_id}/users"
        )
        return [WorkspaceUser.model_validate(item) for item in (data or [])]
