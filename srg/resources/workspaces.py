from pathlib import Path
from typing import Any

from pydantic import BaseModel

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg._upload import (
    extension_from_source,
    upload_to_signed_url,
    upload_to_signed_url_async,
)
from srg.schemas.common import FileUploadParameters
from srg.schemas.hub_profile import MinimalHubProfile
from srg.schemas.workspace import (
    Action,
    MinimalAction,
    Workspace,
    WorkspaceSignedUrl,
)


def _build_action_body(
    title: str,
    metadata: Any,
    hub_profile_ids: list[str] | None,
    details: str | None,
) -> dict:
    meta = (
        metadata.model_dump(by_alias=True, exclude_none=True)
        if isinstance(metadata, BaseModel)
        else metadata
    )
    body: dict = {
        "title": title,
        "metadata": meta,
        "hubProfileIds": hub_profile_ids or [],
    }
    if details is not None:
        body["details"] = details
    return body


class WorkspacesResource:
    def __init__(self, http: SyncHTTPClient, workspace_id: str | None = None) -> None:
        self._http = http
        self._workspace_id = workspace_id

    def get(self, workspace_id: str | None = None) -> Workspace:
        """
        Get a workspace by ID.

        Retrieves full workspace details, including its name, cover image,
        seat usage, subscription plan, and the list of hub profiles it contains.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            Workspace object with subscription and hub profile details.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        workspace = client.workspaces.get()
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
        """
        wid = workspace_id or self._workspace_id
        data = self._http.get(f"/api/v1/workspaces/{wid}")
        return Workspace.model_validate(data)

    def update(
        self,
        workspace_id: str | None = None,
        *,
        name: str,
        cover_image: str | Path | None = None,
        cover: FileUploadParameters | None = None,
    ) -> Workspace | WorkspaceSignedUrl:
        """
        Update the workspace's name and cover image.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image and returns the updated
        :class:`~srg.schemas.workspace.Workspace`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.FileUploadParameters`. The API returns
        :class:`~srg.schemas.workspace.WorkspaceSignedUrl` with a signed URL
        so you can upload the image yourself.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            name: New display name for the workspace.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).

        Returns:
            :class:`~srg.schemas.workspace.Workspace` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.workspace.WorkspaceSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        workspace = client.workspaces.update(
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
        """
        wid = workspace_id or self._workspace_id
        if cover_image is not None and cover is None:
            cover = FileUploadParameters(
                extension=extension_from_source(cover_image),
                generate_signed_url=True,
            )
        body: dict = {"name": name}
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)
        data = self._http.put(f"/api/v1/workspaces/{wid}", json=body)
        result = WorkspaceSignedUrl.model_validate(data)

        if cover_image is not None and result.cover_signed_url is not None:
            upload_to_signed_url(result.cover_signed_url.url, cover_image)

        if cover_image is not None:
            return self.get(wid)
        return result

    def get_hub_profiles(
        self, workspace_id: str | None = None
    ) -> list[MinimalHubProfile]:
        """
        Get all hub profiles in a workspace.

        Returns a minimal representation of each hub profile that belongs to the
        given workspace. Use ``hub_profiles.get(id)`` to fetch full details for
        a specific profile.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            List of MinimalHubProfile objects.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        profiles = client.workspaces.get_hub_profiles()
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
        """
        wid = workspace_id or self._workspace_id
        data = self._http.get(f"/api/v1/workspaces/{wid}/hub-profiles")
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    def create_action(
        self,
        workspace_id: str | None = None,
        *,
        title: str,
        metadata: Any,  # noqa: ANN401
        hub_profile_ids: list[str] | None = None,
        details: str | None = None,
    ) -> str:
        """
        Create an automation action for a workspace.

        Actions are triggered automatically by platform events such as a user
        completing content. The ``metadata`` object defines the action type and
        its configuration (e.g. a webhook URL for
        ``ProgressionUpdatedMetadata``).

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            title: Display title for the action.
            metadata: Action metadata object (e.g. ``ProgressionUpdatedMetadata``).
                Must be a Pydantic model or a plain dict matching the backend schema.
            hub_profile_ids: IDs of hub profiles to associate the action with.
                The action will fire for events on these profiles. Defaults to all.
            details: Optional description of what the action does.

        Returns:
            ID of the newly created action.

        Example:
        ```python
        from sdk.schemas.workspace import ProgressionUpdatedMetadata

        client = SRGClient(api_key="srgplus_your_key")
        action_id = client.workspaces.create_action(
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
        """
        wid = workspace_id or self._workspace_id
        body = _build_action_body(title, metadata, hub_profile_ids, details)
        data = self._http.post(f"/api/v1/workspaces/{wid}/actions", json=body)
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    def list_actions(self, workspace_id: str | None = None) -> list[MinimalAction]:
        """
        List all automation actions for a workspace.

        Returns a minimal summary of every action configured on the workspace.
        Use ``get_action`` to retrieve full details including hub profile
        associations and metadata.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            List of MinimalAction objects.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        actions = client.workspaces.list_actions()
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
        """
        wid = workspace_id or self._workspace_id
        data = self._http.get(f"/api/v1/workspaces/{wid}/actions")
        return [MinimalAction.model_validate(item) for item in (data or [])]

    def get_action(self, action_id: str, *, workspace_id: str | None = None) -> Action:
        """
        Get an automation action by ID.

        Retrieves the full details of an action, including its metadata and
        the list of associated hub profiles.

        Args:
            action_id: ID of the action to retrieve.
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            Action object with metadata and hub profile associations.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        action = client.workspaces.get_action("01965f7a-0000-7000-8000-000000000040")
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
        """
        wid = workspace_id or self._workspace_id
        data = self._http.get(f"/api/v1/workspaces/{wid}/actions/{action_id}")
        return Action.model_validate(data)

    def update_action(
        self,
        action_id: str,
        *,
        workspace_id: str | None = None,
        title: str,
        metadata: Any,  # noqa: ANN401
        hub_profile_ids: list[str] | None = None,
        details: str | None = None,
    ) -> dict | None:
        """
        Update an automation action.

        Replaces the action's title, metadata, hub profile associations, and
        optional description. All fields are overwritten (not patched).

        Args:
            action_id: ID of the action to update.
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            title: New display title.
            metadata: New metadata object (e.g. ``ProgressionUpdatedMetadata``).
            hub_profile_ids: New list of hub profile IDs. Replaces the existing list.
            details: New description. Omit to clear the current description.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        from sdk.schemas.workspace import ProgressionUpdatedMetadata

        client = SRGClient(api_key="srgplus_your_key")
        client.workspaces.update_action(
            "01965f7a-0000-7000-8000-000000000040",
            title="Notify on completion (updated)",
            metadata=ProgressionUpdatedMetadata(
                webhook_url="https://hooks.example.com/srg-v2"
            ),
            hub_profile_ids=["01965f7a-0000-7000-8000-000000000002"],
        )
        ```
        """
        wid = workspace_id or self._workspace_id
        body = _build_action_body(title, metadata, hub_profile_ids, details)
        return self._http.put(
            f"/api/v1/workspaces/{wid}/actions/{action_id}",
            json=body,
        )

    def delete_action(self, action_id: str, *, workspace_id: str | None = None) -> None:
        """
        Delete an automation action.

        Permanently removes the action from the workspace. Any future events
        that would have triggered it will no longer fire the webhook.

        Args:
            action_id: ID of the action to delete.
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.workspaces.delete_action("01965f7a-0000-7000-8000-000000000040")
        ```
        """
        wid = workspace_id or self._workspace_id
        self._http.delete(f"/api/v1/workspaces/{wid}/actions/{action_id}")


class AsyncWorkspacesResource:
    def __init__(self, http: AsyncHTTPClient, workspace_id: str | None = None) -> None:
        self._http = http
        self._workspace_id = workspace_id

    async def get(self, workspace_id: str | None = None) -> Workspace:
        """
        Get a workspace by ID.

        Retrieves full workspace details, including its name, cover image,
        seat usage, subscription plan, and the list of hub profiles it contains.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            Workspace object with subscription and hub profile details.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            workspace = await client.workspaces.get()
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
        """
        wid = workspace_id or self._workspace_id
        data = await self._http.get(f"/api/v1/workspaces/{wid}")
        return Workspace.model_validate(data)

    async def update(
        self,
        workspace_id: str | None = None,
        *,
        name: str,
        cover_image: str | Path | None = None,
        cover: FileUploadParameters | None = None,
    ) -> Workspace | WorkspaceSignedUrl:
        """
        Update the workspace's name and cover image.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image and returns the updated
        :class:`~srg.schemas.workspace.Workspace`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.FileUploadParameters`. The API returns
        :class:`~srg.schemas.workspace.WorkspaceSignedUrl` with a signed URL
        so you can upload the image yourself.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            name: New display name for the workspace.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).

        Returns:
            :class:`~srg.schemas.workspace.Workspace` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.workspace.WorkspaceSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            workspace = await client.workspaces.update(
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
        """
        wid = workspace_id or self._workspace_id
        if cover_image is not None and cover is None:
            cover = FileUploadParameters(
                extension=extension_from_source(cover_image),
                generate_signed_url=True,
            )
        body: dict = {"name": name}
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)
        data = await self._http.put(f"/api/v1/workspaces/{wid}", json=body)
        result = WorkspaceSignedUrl.model_validate(data)

        if cover_image is not None and result.cover_signed_url is not None:
            await upload_to_signed_url_async(result.cover_signed_url.url, cover_image)

        if cover_image is not None:
            return await self.get(wid)
        return result

    async def get_hub_profiles(
        self, workspace_id: str | None = None
    ) -> list[MinimalHubProfile]:
        """
        Get all hub profiles in a workspace.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            List of MinimalHubProfile objects.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            profiles = await client.workspaces.get_hub_profiles()
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
        """
        wid = workspace_id or self._workspace_id
        data = await self._http.get(f"/api/v1/workspaces/{wid}/hub-profiles")
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    async def create_action(
        self,
        workspace_id: str | None = None,
        *,
        title: str,
        metadata: Any,  # noqa: ANN401
        hub_profile_ids: list[str] | None = None,
        details: str | None = None,
    ) -> str:
        """
        Create an automation action for a workspace.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            title: Display title for the action.
            metadata: Action metadata object (e.g. ``ProgressionUpdatedMetadata``).
            hub_profile_ids: IDs of hub profiles to associate the action with.
                Defaults to all.
            details: Optional description of what the action does.

        Returns:
            ID of the newly created action.

        Example:
        ```python
        from sdk.schemas.workspace import ProgressionUpdatedMetadata

        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            action_id = await client.workspaces.create_action(
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
        """
        wid = workspace_id or self._workspace_id
        body = _build_action_body(title, metadata, hub_profile_ids, details)
        data = await self._http.post(f"/api/v1/workspaces/{wid}/actions", json=body)
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    async def list_actions(
        self, workspace_id: str | None = None
    ) -> list[MinimalAction]:
        """
        List all automation actions for a workspace.

        Args:
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            List of MinimalAction objects.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            actions = await client.workspaces.list_actions()
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
        """
        wid = workspace_id or self._workspace_id
        data = await self._http.get(f"/api/v1/workspaces/{wid}/actions")
        return [MinimalAction.model_validate(item) for item in (data or [])]

    async def get_action(
        self, action_id: str, *, workspace_id: str | None = None
    ) -> Action:
        """
        Get an automation action by ID.

        Args:
            action_id: ID of the action to retrieve.
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Returns:
            Action object with metadata and hub profile associations.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            action = await client.workspaces.get_action(
                "01965f7a-0000-7000-8000-000000000040"
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
        """
        wid = workspace_id or self._workspace_id
        data = await self._http.get(f"/api/v1/workspaces/{wid}/actions/{action_id}")
        return Action.model_validate(data)

    async def update_action(
        self,
        action_id: str,
        *,
        workspace_id: str | None = None,
        title: str,
        metadata: Any,  # noqa: ANN401
        hub_profile_ids: list[str] | None = None,
        details: str | None = None,
    ) -> dict | None:
        """
        Update an automation action.

        Args:
            action_id: ID of the action to update.
            workspace_id: ID of the workspace. Uses the client's default if omitted.
            title: New display title.
            metadata: New metadata object (e.g. ``ProgressionUpdatedMetadata``).
            hub_profile_ids: New list of hub profile IDs. Replaces the existing list.
            details: New description. Omit to clear the current description.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        from sdk.schemas.workspace import ProgressionUpdatedMetadata

        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.workspaces.update_action(
                "01965f7a-0000-7000-8000-000000000040",
                title="Notify on completion (updated)",
                metadata=ProgressionUpdatedMetadata(
                    webhook_url="https://hooks.example.com/srg-v2"
                ),
            )
        ```
        """
        wid = workspace_id or self._workspace_id
        body = _build_action_body(title, metadata, hub_profile_ids, details)
        return await self._http.put(
            f"/api/v1/workspaces/{wid}/actions/{action_id}",
            json=body,
        )

    async def delete_action(
        self, action_id: str, *, workspace_id: str | None = None
    ) -> None:
        """
        Delete an automation action.

        Args:
            action_id: ID of the action to delete.
            workspace_id: ID of the workspace. Uses the client's default if omitted.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.workspaces.delete_action(
                "01965f7a-0000-7000-8000-000000000040"
            )
        ```
        """
        wid = workspace_id or self._workspace_id
        await self._http.delete(f"/api/v1/workspaces/{wid}/actions/{action_id}")
