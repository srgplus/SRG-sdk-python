import builtins

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.exceptions import SRGError
from srg.schemas.invitation import (
    Invitation,
    InviteToHubWithLink,
    InviteToTarget,
)


class InvitationsResource:
    def __init__(self, registry: dict[str, SyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> SyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    def list(
        self, target_type: str, target_id: str, *, workspace_id: str
    ) -> list[Invitation]:
        """
        List all pending invitations for a target.

        Returns all open (not yet accepted or expired) invitations associated
        with the given target resource.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.

        Returns:
            List of Invitation objects.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        invitations = client.invitations.list(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        [
            Invitation(
                id="01965f7a-0000-7000-8000-000000000020",
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                email="alice@example.com",
                role_id=2,
                status="Pending",
            ),
        ]
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/invitations/{target_type}/{target_id}"
        )
        return [Invitation.model_validate(item) for item in (data or [])]

    def invite(
        self,
        target_type: str,
        target_id: str,
        *,
        role_id: int,
        emails: builtins.list[str],
        workspace_id: str,
    ) -> InviteToTarget:
        """
        Send email invitations to join a target with the given role.

        Sends invitation emails to one or more addresses. Each invited user
        will receive a link to accept the invitation and gain the specified role.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            role_id: Role ID to assign to the invited users upon acceptance.
            emails: List of email addresses to invite.

        Returns:
            InviteToTarget with the list of created invitation IDs.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        result = client.invitations.invite(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            role_id=2,
            emails=["alice@example.com", "bob@example.com"],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        InviteToTarget(
            ids=[
                "01965f7a-0000-7000-8000-000000000021",
                "01965f7a-0000-7000-8000-000000000022",
            ],
        )
        ```
        """
        data = self._get_http(workspace_id).post(
            f"/api/v1/invitations/{target_type}/{target_id}",
            json={"roleId": role_id, "emails": emails},
        )
        return InviteToTarget.model_validate(data)

    def invite_with_link(
        self,
        target_type: str,
        target_id: str,
        *,
        role_id: int,
        email: str,
        workspace_id: str,
    ) -> InviteToHubWithLink:
        """
        Create an invitation link for a single email address.

        Generates a shareable invitation link for the specified email.
        The link grants the recipient access to the target with the given role
        when followed.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            role_id: Role ID to assign upon acceptance.
            email: Email address of the recipient.

        Returns:
            InviteToHubWithLink containing the invitation ID and access link.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        result = client.invitations.invite_with_link(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            role_id=2,
            email="alice@example.com",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        print(result.access_link)
        ```

        Example response:
        ```python
        InviteToHubWithLink(
            invitation_id="01965f7a-0000-7000-8000-000000000021",
            access_link="https://app.srgplus.com/invite/abc123xyz",
        )
        ```
        """
        data = self._get_http(workspace_id).post(
            f"/api/v1/invitations/{target_type}/{target_id}/link",
            json={"roleId": role_id, "email": email},
        )
        return InviteToHubWithLink.model_validate(data)

    def update(
        self,
        target_type: str,
        target_id: str,
        invitation_id: str,
        *,
        role_id: int | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the role assigned to an existing invitation.

        Changes the role that will be granted to the invited user upon
        acceptance. Only pending invitations can be updated.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            invitation_id: ID of the invitation to update.
            role_id: New role ID to assign. Unchanged if not provided.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.invitations.update(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            "01965f7a-0000-7000-8000-000000000021",
            role_id=3,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body: dict = {}
        if role_id is not None:
            body["roleId"] = role_id
        return self._get_http(workspace_id).put(
            f"/api/v1/invitations/{target_type}/{target_id}/{invitation_id}",
            json=body,
        )

    def delete(
        self, target_type: str, target_id: str, invitation_id: str, *, workspace_id: str
    ) -> None:
        """
        Cancel and delete an invitation.

        Permanently removes the invitation. The invited user will no longer
        be able to accept it via email or link.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            invitation_id: ID of the invitation to delete.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.invitations.delete(
            "HubProfile",
            "01965f7a-0000-7000-8000-000000000002",
            "01965f7a-0000-7000-8000-000000000021",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/invitations/{target_type}/{target_id}/{invitation_id}"
        )


class AsyncInvitationsResource:
    def __init__(self, registry: dict[str, AsyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> AsyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    async def list(
        self, target_type: str, target_id: str, *, workspace_id: str
    ) -> list[Invitation]:
        """
        List all pending invitations for a target.

        Returns all open (not yet accepted or expired) invitations associated
        with the given target resource.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.

        Returns:
            List of Invitation objects.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            invitations = await client.invitations.list(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        [
            Invitation(
                id="01965f7a-0000-7000-8000-000000000020",
                target_id="01965f7a-0000-7000-8000-000000000002",
                target_type="HubProfile",
                email="alice@example.com",
                role_id=2,
                status="Pending",
            ),
        ]
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/invitations/{target_type}/{target_id}"
        )
        return [Invitation.model_validate(item) for item in (data or [])]

    async def invite(
        self,
        target_type: str,
        target_id: str,
        *,
        role_id: int,
        emails: builtins.list[str],
        workspace_id: str,
    ) -> InviteToTarget:
        """
        Send email invitations to join a target with the given role.

        Sends invitation emails to one or more addresses. Each invited user
        will receive a link to accept the invitation and gain the specified role.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            role_id: Role ID to assign to the invited users upon acceptance.
            emails: List of email addresses to invite.

        Returns:
            InviteToTarget with the list of created invitation IDs.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            result = await client.invitations.invite(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                role_id=2,
                emails=["alice@example.com", "bob@example.com"],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        InviteToTarget(
            ids=[
                "01965f7a-0000-7000-8000-000000000021",
                "01965f7a-0000-7000-8000-000000000022",
            ],
        )
        ```
        """
        data = await self._get_http(workspace_id).post(
            f"/api/v1/invitations/{target_type}/{target_id}",
            json={"roleId": role_id, "emails": emails},
        )
        return InviteToTarget.model_validate(data)

    async def invite_with_link(
        self,
        target_type: str,
        target_id: str,
        *,
        role_id: int,
        email: str,
        workspace_id: str,
    ) -> InviteToHubWithLink:
        """
        Create an invitation link for a single email address.

        Generates a shareable invitation link for the specified email.
        The link grants the recipient access to the target with the given role
        when followed.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            role_id: Role ID to assign upon acceptance.
            email: Email address of the recipient.

        Returns:
            InviteToHubWithLink containing the invitation ID and access link.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            result = await client.invitations.invite_with_link(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                role_id=2,
                email="alice@example.com",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        InviteToHubWithLink(
            invitation_id="01965f7a-0000-7000-8000-000000000021",
            access_link="https://app.srgplus.com/invite/abc123xyz",
        )
        ```
        """
        data = await self._get_http(workspace_id).post(
            f"/api/v1/invitations/{target_type}/{target_id}/link",
            json={"roleId": role_id, "email": email},
        )
        return InviteToHubWithLink.model_validate(data)

    async def update(
        self,
        target_type: str,
        target_id: str,
        invitation_id: str,
        *,
        role_id: int | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the role assigned to an existing invitation.

        Changes the role that will be granted to the invited user upon
        acceptance. Only pending invitations can be updated.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            invitation_id: ID of the invitation to update.
            role_id: New role ID to assign. Unchanged if not provided.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.invitations.update(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                "01965f7a-0000-7000-8000-000000000021",
                role_id=3,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body: dict = {}
        if role_id is not None:
            body["roleId"] = role_id
        return await self._get_http(workspace_id).put(
            f"/api/v1/invitations/{target_type}/{target_id}/{invitation_id}",
            json=body,
        )

    async def delete(
        self,
        target_type: str,
        target_id: str,
        invitation_id: str,
        workspace_id: str,
    ) -> None:
        """
        Cancel and delete an invitation.

        Permanently removes the invitation. The invited user will no longer
        be able to accept it via email or link.

        Args:
            target_type: Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
            target_id: ID of the target resource.
            invitation_id: ID of the invitation to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.invitations.delete(
                "HubProfile",
                "01965f7a-0000-7000-8000-000000000002",
                "01965f7a-0000-7000-8000-000000000021",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/invitations/{target_type}/{target_id}/{invitation_id}"
        )
