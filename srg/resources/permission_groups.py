import builtins

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.exceptions import SRGError
from srg.schemas.permission import (
    GetPermissionGroup,
    PermissionGroup,
)


class PermissionGroupsResource:
    def __init__(self, registry: dict[str, SyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> SyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    def create(
        self, target_type: str, target_id: str, *, name: str, workspace_id: str
    ) -> str:
        """
        Create a new permission group on a target.

        Permission groups allow you to batch-assign roles to multiple users
        on a hub profile or workspace. Once created, users can be added to
        the group and will inherit its permissions.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            name: Display name for the new permission group.

        Returns:
            ID of the newly created permission group.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        group_id = client.permission_groups.create(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            name="Content Editors",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000030"
        ```
        """
        data = self._get_http(workspace_id).post(
            f"/api/v1/permission-groups/{target_type}/{target_id}",
            json={"name": name},
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    def list(
        self, target_type: str, target_id: str, *, workspace_id: str
    ) -> list[PermissionGroup]:
        """
        List all permission groups for a target.

        Returns all permission groups defined on the given hub profile or
        workspace, along with their member counts.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.

        Returns:
            List of PermissionGroup objects.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        groups = client.permission_groups.list(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/permission-groups/{target_type}/{target_id}/list"
        )
        return [PermissionGroup.model_validate(item) for item in (data or [])]

    def get(self, group_id: str, *, workspace_id: str) -> GetPermissionGroup:
        """
        Get a permission group by ID, including its members.

        Retrieves the full details of a permission group and the list of
        users currently in the group.

        Args:
            group_id: ID of the permission group.

        Returns:
            GetPermissionGroup containing the group metadata and its members.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        group = client.permission_groups.get(
            "01965f7a-0000-7000-8000-000000000030",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
                PermissionGroupUser(
                    id="01965f7a-0000-7000-8000-000000000008",
                    email="jane.doe@example.com",
                    first_name="Jane",
                    last_name="Doe",
                ),
            ],
        )
        ```
        """
        data = self._get_http(workspace_id).get(f"/api/v1/permission-groups/{group_id}")
        return GetPermissionGroup.model_validate(data)

    def update(self, group_id: str, *, name: str, workspace_id: str) -> dict | None:
        """
        Update the name of a permission group.

        Renames the permission group. Does not affect the group's members
        or their permissions.

        Args:
            group_id: ID of the permission group.
            name: New display name for the group.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permission_groups.update(
            "01965f7a-0000-7000-8000-000000000030",
            name="Senior Editors",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).put(
            f"/api/v1/permission-groups/{group_id}", json={"name": name}
        )

    def delete(self, group_id: str, *, workspace_id: str) -> None:
        """
        Delete a permission group.

        Permanently removes the permission group. Users who were members of
        the group will lose any permissions they inherited from it.

        Args:
            group_id: ID of the permission group to delete.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permission_groups.delete(
            "01965f7a-0000-7000-8000-000000000030",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(f"/api/v1/permission-groups/{group_id}")

    def add_users(
        self, group_id: str, *, user_ids: builtins.list[str], workspace_id: str
    ) -> dict | None:
        """
        Add users to a permission group.

        Adds one or more users to the group. They will immediately inherit
        the group's permissions on the associated target.

        Args:
            group_id: ID of the permission group.
            user_ids: List of user IDs to add to the group.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permission_groups.add_users(
            "01965f7a-0000-7000-8000-000000000030",
            user_ids=[
                "01965f7a-0000-7000-8000-000000000007",
                "01965f7a-0000-7000-8000-000000000008",
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).post(
            f"/api/v1/permission-groups/{group_id}",
            json={"userIds": user_ids},
        )

    def remove_user(self, group_id: str, user_id: str, *, workspace_id: str) -> None:
        """
        Remove a user from a permission group.

        Removes the user from the group. They will immediately lose the
        permissions they inherited from it on the associated target.

        Args:
            group_id: ID of the permission group.
            user_id: ID of the user to remove.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.permission_groups.remove_user(
            "01965f7a-0000-7000-8000-000000000030",
            "01965f7a-0000-7000-8000-000000000007",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/permission-groups/{group_id}/{user_id}"
        )


class AsyncPermissionGroupsResource:
    def __init__(self, registry: dict[str, AsyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> AsyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    async def create(
        self, target_type: str, target_id: str, *, name: str, workspace_id: str
    ) -> str:
        """
        Create a new permission group on a target.

        Permission groups allow you to batch-assign roles to multiple users
        on a hub profile or workspace. Once created, users can be added to
        the group and will inherit its permissions.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            name: Display name for the new permission group.

        Returns:
            ID of the newly created permission group.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            group_id = await client.permission_groups.create(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                name="Content Editors",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000030"
        ```
        """
        data = await self._get_http(workspace_id).post(
            f"/api/v1/permission-groups/{target_type}/{target_id}",
            json={"name": name},
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    async def list(
        self, target_type: str, target_id: str, *, workspace_id: str
    ) -> list[PermissionGroup]:
        """
        List all permission groups for a target.

        Returns all permission groups defined on the given hub profile or
        workspace, along with their member counts.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.

        Returns:
            List of PermissionGroup objects.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            groups = await client.permission_groups.list(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permission-groups/{target_type}/{target_id}/list"
        )
        return [PermissionGroup.model_validate(item) for item in (data or [])]

    async def get(self, group_id: str, *, workspace_id: str) -> GetPermissionGroup:
        """
        Get a permission group by ID, including its members.

        Retrieves the full details of a permission group and the list of
        users currently in the group.

        Args:
            group_id: ID of the permission group.

        Returns:
            GetPermissionGroup containing the group metadata and its members.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            group = await client.permission_groups.get(
                "01965f7a-0000-7000-8000-000000000030",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/permission-groups/{group_id}"
        )
        return GetPermissionGroup.model_validate(data)

    async def update(
        self, group_id: str, *, name: str, workspace_id: str
    ) -> dict | None:
        """
        Update the name of a permission group.

        Renames the permission group. Does not affect the group's members
        or their permissions.

        Args:
            group_id: ID of the permission group.
            name: New display name for the group.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permission_groups.update(
                "01965f7a-0000-7000-8000-000000000030",
                name="Senior Editors",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).put(
            f"/api/v1/permission-groups/{group_id}", json={"name": name}
        )

    async def delete(self, group_id: str, *, workspace_id: str) -> None:
        """
        Delete a permission group.

        Permanently removes the permission group. Users who were members of
        the group will lose any permissions they inherited from it.

        Args:
            group_id: ID of the permission group to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permission_groups.delete(
                "01965f7a-0000-7000-8000-000000000030",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/permission-groups/{group_id}"
        )

    async def add_users(
        self,
        group_id: str,
        *,
        user_ids: builtins.list[str],
        workspace_id: str,
    ) -> dict | None:
        """
        Add users to a permission group.

        Adds one or more users to the group. They will immediately inherit
        the group's permissions on the associated target.

        Args:
            group_id: ID of the permission group.
            user_ids: List of user IDs to add to the group.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permission_groups.add_users(
                "01965f7a-0000-7000-8000-000000000030",
                user_ids=[
                    "01965f7a-0000-7000-8000-000000000007",
                    "01965f7a-0000-7000-8000-000000000008",
                ],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).post(
            f"/api/v1/permission-groups/{group_id}",
            json={"userIds": user_ids},
        )

    async def remove_user(
        self, group_id: str, user_id: str, *, workspace_id: str
    ) -> None:
        """
        Remove a user from a permission group.

        Removes the user from the group. They will immediately lose the
        permissions they inherited from it on the associated target.

        Args:
            group_id: ID of the permission group.
            user_id: ID of the user to remove.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.permission_groups.remove_user(
                "01965f7a-0000-7000-8000-000000000030",
                "01965f7a-0000-7000-8000-000000000007",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/permission-groups/{group_id}/{user_id}"
        )
