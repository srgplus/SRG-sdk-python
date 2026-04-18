import builtins
from pathlib import Path

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg._upload import (
    extension_from_source,
    upload_to_signed_url,
    upload_to_signed_url_async,
)
from srg.exceptions import SRGError
from srg.schemas.common import AvailabilityLevel, FileUploadParameters
from srg.schemas.hub_profile import (
    ActionButtonUpsert,
    GetHubProfile,
    HubProfileFilter,
    HubProfileSignedUrls,
    MinimalHubProfile,
)

_AVAILABILITY_LEVEL = {"Public": 0, "Private": 1}


class HubProfilesResource:
    def __init__(self, http: SyncHTTPClient, workspace_id: str | None = None) -> None:
        self._http = http
        self._workspace_id = workspace_id

    def create(
        self,
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
        widgets: list[dict] | None = None,
    ) -> GetHubProfile | HubProfileSignedUrls:
        """
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

        Args:
            name: Display name for the hub profile.
            user_name: Unique username / URL slug for the hub profile.
            sub_name: Optional subtitle shown below the name.
            description: Optional text description.
            primary_url: Optional external URL shown on the profile.
            availability_level: Visibility — ``"Public"`` (default) or
                ``"Private"``.
            app_clip_on: Whether to enable iOS App Clip. Defaults to False.
            buttons: List of action buttons to display on the profile page.
            avatar_image: Local path or ``http(s)://`` URL of the avatar image.
                The extension is derived automatically. Triggers auto-upload.
            cover_image: Local path or ``http(s)://`` URL of the cover image.
                The extension is derived automatically. Triggers auto-upload.
            avatar_extension: File extension for the avatar image (e.g.
                ``"jpg"``). Used in manual mode when ``avatar_image`` is not
                provided.
            cover_extension: File extension for the cover image. Used in manual
                mode when ``cover_image`` is not provided.
            workspace_id: Workspace to create the profile in. Uses the client's
                default workspace if omitted.
            widgets: Profile widget configuration objects.

        Returns:
            :class:`~srg.schemas.hub_profile.GetHubProfile` when
            ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
            :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
            (manual mode).

        Example:
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
        """
        if avatar_image is not None and avatar_extension is None:
            avatar_extension = extension_from_source(avatar_image)
        if cover_image is not None and cover_extension is None:
            cover_extension = extension_from_source(cover_image)

        body: dict = {
            "name": name,
            "userName": user_name,
            "availabilityLevel": _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            ),
            "appClipOn": app_clip_on,
            "buttons": [
                b.model_dump(by_alias=True, exclude_none=True) for b in (buttons or [])
            ],
        }
        if sub_name is not None:
            body["subName"] = sub_name
        if description is not None:
            body["description"] = description
        if primary_url is not None:
            body["primaryUrl"] = primary_url
        if avatar_extension is not None:
            body["avatarExtension"] = avatar_extension
        if cover_extension is not None:
            body["coverExtension"] = cover_extension
        effective_workspace_id = workspace_id or self._workspace_id
        if effective_workspace_id is not None:
            body["workspaceId"] = effective_workspace_id
        if widgets is not None:
            body["widgets"] = widgets

        data = self._http.post("/api/v1/hub-profiles", json=body)
        result = HubProfileSignedUrls.model_validate(data)

        if avatar_image is not None and result.avatar_signed_url is not None:
            upload_to_signed_url(result.avatar_signed_url.url, avatar_image)
        if cover_image is not None and result.cover_signed_url is not None:
            upload_to_signed_url(result.cover_signed_url.url, cover_image)

        if avatar_image is not None or cover_image is not None:
            return self.get(result.id)
        return result

    def get(self, hub_profile_id: str) -> GetHubProfile:
        """
        Get a hub profile by ID.

        Retrieves the full details of a hub profile, including its name,
        username, description, avatar, cover, action buttons, and widgets.

        Args:
            hub_profile_id: ID of the hub profile to retrieve.

        Returns:
            GetHubProfile with all profile fields.

        Example:
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
        """
        data = self._http.get(f"/api/v1/hub-profiles/{hub_profile_id}")
        return GetHubProfile.model_validate(data)

    def get_by_username(self, username: str) -> GetHubProfile:
        """
        Get a hub profile by its username.

        Retrieves the full details of a hub profile using its URL slug
        instead of its ID. Useful when you only know the public-facing
        username of the profile.

        Args:
            username: The hub profile's username / URL slug (e.g.
                ``"acme-academy"``).

        Returns:
            GetHubProfile with all profile fields.

        Example:
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
        """
        data = self._http.get(f"/api/v1/hub-profiles/username/{username}")
        return GetHubProfile.model_validate(data)

    def list(self) -> builtins.list[MinimalHubProfile]:
        """
        List all hub profiles in the current workspace.

        Returns a minimal summary of each hub profile in the workspace
        associated with the client's API key.

        Returns:
            List of MinimalHubProfile objects.

        Example:
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
        """
        data = self._http.get(f"/api/v1/workspaces/{self._workspace_id}/hub-profiles")
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    def list_managed(self) -> builtins.list[MinimalHubProfile]:
        """
        List all hub profiles managed by the current user.

        Returns every hub profile for which the current API key user has
        an Admin or Editor role. Useful for scoping operations to profiles
        the caller can modify.

        Returns:
            List of MinimalHubProfile objects.

        Example:
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
        """
        data = self._http.get("/api/v1/hub-profiles/managed")
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    def update(
        self,
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
        widgets: builtins.list[dict] | None = None,
    ) -> GetHubProfile | HubProfileSignedUrls:
        """
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

        Args:
            hub_profile_id: ID of the hub profile to update.
            name: New display name.
            user_name: New username / URL slug.
            sub_name: New subtitle. Pass ``None`` to clear.
            description: New description text. Pass ``None`` to clear.
            primary_url: New primary external URL. Pass ``None`` to clear.
            availability_level: New visibility — ``"Public"`` or ``"Private"``.
            app_clip_on: Whether to enable iOS App Clip.
            buttons: New list of action buttons. Replaces the existing list.
            avatar_image: Local path or ``http(s)://`` URL of the new avatar
                image. Triggers auto-upload.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            avatar: Avatar upload parameters (manual mode).
            cover: Cover upload parameters (manual mode).
            widgets: New widget configuration. Replaces the existing widgets.

        Returns:
            :class:`~srg.schemas.hub_profile.GetHubProfile` when
            ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
            :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
            (manual mode).

        Example:
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
        """
        if avatar_image is not None and avatar is None:
            avatar = FileUploadParameters(
                extension=extension_from_source(avatar_image),
                generate_signed_url=True,
            )
        if cover_image is not None and cover is None:
            cover = FileUploadParameters(
                extension=extension_from_source(cover_image),
                generate_signed_url=True,
            )

        body: dict = {
            "name": name,
            "userName": user_name,
            "availabilityLevel": _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            ),
            "appClipOn": app_clip_on,
            "buttons": [
                b.model_dump(by_alias=True, exclude_none=True) for b in (buttons or [])
            ],
        }
        if sub_name is not None:
            body["subName"] = sub_name
        if description is not None:
            body["description"] = description
        if primary_url is not None:
            body["primaryUrl"] = primary_url
        if avatar is not None:
            body["avatar"] = avatar.model_dump(by_alias=True, exclude_none=True)
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)
        if widgets is not None:
            body["widgets"] = widgets

        data = self._http.put(f"/api/v1/hub-profiles/{hub_profile_id}", json=body)
        result = HubProfileSignedUrls.model_validate(data)

        if avatar_image is not None and result.avatar_signed_url is not None:
            upload_to_signed_url(result.avatar_signed_url.url, avatar_image)
        if cover_image is not None and result.cover_signed_url is not None:
            upload_to_signed_url(result.cover_signed_url.url, cover_image)

        if avatar_image is not None or cover_image is not None:
            return self.get(hub_profile_id)
        return result

    def archive(self, hub_profile_id: str) -> dict | None:
        """
        Archive a hub profile.

        Moves the hub profile to an archived state. Archived profiles are
        hidden from public listings but can be restored. Content within the
        profile is preserved.

        Args:
            hub_profile_id: ID of the hub profile to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.archive("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/archive")

    def restore(self, hub_profile_id: str) -> dict | None:
        """
        Restore a previously archived hub profile.

        Makes the hub profile active again after it was archived. The profile
        will reappear in public listings according to its visibility setting.

        Args:
            hub_profile_id: ID of the hub profile to restore.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.restore("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/restore")

    def delete(self, hub_profile_id: str) -> None:
        """
        Permanently delete a hub profile.

        Removes the hub profile and all of its data. This action is
        irreversible.

        Args:
            hub_profile_id: ID of the hub profile to delete.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.delete("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        self._http.delete(f"/api/v1/hub-profiles/{hub_profile_id}")

    def join(self, hub_profile_id: str) -> dict | None:
        """
        Join a public hub profile as the current user.

        Registers the current API key user as a member of the hub profile.
        Only applicable to profiles with ``availability_level == "Public"``.

        Args:
            hub_profile_id: ID of the hub profile to join.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.join("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/join")

    def filter(
        self,
        *,
        ids: builtins.list[str],
        availability_level: AvailabilityLevel | None = None,
    ) -> builtins.list[HubProfileFilter]:
        """
        Get minimal info for a list of hub profile IDs.

        Batch-fetches lightweight hub profile data (ID, name, username,
        avatar) for a list of known IDs. Optionally filter to a specific
        visibility level.

        Args:
            ids: List of hub profile IDs to look up.
            availability_level: If provided, only returns profiles matching
                this visibility level (``"Public"`` or ``"Private"``).

        Returns:
            List of HubProfileFilter objects (minimal representation).

        Example:
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
        """
        body: dict = {"ids": ids}
        if availability_level is not None:
            body["availabilityLevel"] = _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            )
        data = self._http.post("/api/v1/hub-profiles/filter", json=body)
        return [HubProfileFilter.model_validate(item) for item in (data or [])]

    def move_to_workspace(self, hub_profile_id: str, workspace_id: str) -> dict | None:
        """
        Move a hub profile to a different workspace.

        Transfers ownership of the hub profile to the specified workspace.
        All existing content, channels, and permissions are preserved.

        Args:
            hub_profile_id: ID of the hub profile to move.
            workspace_id: ID of the destination workspace.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.move_to_workspace(
            "01965f7a-0000-7000-8000-000000000002",
            "01965f7a-0000-7000-8000-000000000050",
        )
        ```
        """
        return self._http.post(
            f"/api/v1/hub-profiles/{hub_profile_id}/move-to/workspaces/{workspace_id}"
        )

    def turn_on_community(self, hub_profile_id: str) -> dict | None:
        """
        Enable community features for a hub profile.

        Activates the community module, which allows members to interact
        with each other through posts, comments, and reactions within the
        hub profile.

        Args:
            hub_profile_id: ID of the hub profile to enable community for.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.hub_profiles.turn_on_community("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return self._http.post(
            f"/api/v1/hub-profiles/{hub_profile_id}/turn-on-community"
        )


class AsyncHubProfilesResource:
    def __init__(self, http: AsyncHTTPClient, workspace_id: str | None = None) -> None:
        self._http = http
        self._workspace_id = workspace_id

    async def create(
        self,
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
        widgets: list[dict] | None = None,
    ) -> GetHubProfile | HubProfileSignedUrls:
        """
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

        Args:
            name: Display name for the hub profile.
            user_name: Unique username / URL slug for the hub profile.
            sub_name: Optional subtitle shown below the name.
            description: Optional text description.
            primary_url: Optional external URL shown on the profile.
            availability_level: Visibility — ``"Public"`` (default) or
                ``"Private"``.
            app_clip_on: Whether to enable iOS App Clip. Defaults to False.
            buttons: List of action buttons to display on the profile page.
            avatar_image: Local path or ``http(s)://`` URL of the avatar image.
                The extension is derived automatically. Triggers auto-upload.
            cover_image: Local path or ``http(s)://`` URL of the cover image.
                The extension is derived automatically. Triggers auto-upload.
            avatar_extension: File extension for the avatar image (e.g.
                ``"jpg"``). Used in manual mode when ``avatar_image`` is not
                provided.
            cover_extension: File extension for the cover image. Used in manual
                mode when ``cover_image`` is not provided.
            workspace_id: Workspace to create the profile in. Uses the client's
                default workspace if omitted.
            widgets: Profile widget configuration objects.

        Returns:
            :class:`~srg.schemas.hub_profile.GetHubProfile` when
            ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
            :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
            (manual mode).

        Example:
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
        """
        if avatar_image is not None and avatar_extension is None:
            avatar_extension = extension_from_source(avatar_image)
        if cover_image is not None and cover_extension is None:
            cover_extension = extension_from_source(cover_image)

        body: dict = {
            "name": name,
            "userName": user_name,
            "availabilityLevel": _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            ),
            "appClipOn": app_clip_on,
            "buttons": [
                b.model_dump(by_alias=True, exclude_none=True) for b in (buttons or [])
            ],
        }
        if sub_name is not None:
            body["subName"] = sub_name
        if description is not None:
            body["description"] = description
        if primary_url is not None:
            body["primaryUrl"] = primary_url
        if avatar_extension is not None:
            body["avatarExtension"] = avatar_extension
        if cover_extension is not None:
            body["coverExtension"] = cover_extension
        effective_workspace_id = workspace_id or self._workspace_id
        if effective_workspace_id is not None:
            body["workspaceId"] = effective_workspace_id
        if widgets is not None:
            body["widgets"] = widgets

        data = await self._http.post("/api/v1/hub-profiles", json=body)
        result = HubProfileSignedUrls.model_validate(data)

        if avatar_image is not None and result.avatar_signed_url is not None:
            await upload_to_signed_url_async(result.avatar_signed_url.url, avatar_image)
        if cover_image is not None and result.cover_signed_url is not None:
            await upload_to_signed_url_async(result.cover_signed_url.url, cover_image)

        if avatar_image is not None or cover_image is not None:
            return await self.get(result.id)
        return result

    async def get(self, hub_profile_id: str) -> GetHubProfile:
        """
        Get a hub profile by ID.

        Retrieves the full details of a hub profile, including its name,
        username, description, avatar, cover, action buttons, and widgets.

        Args:
            hub_profile_id: ID of the hub profile to retrieve.

        Returns:
            GetHubProfile with all profile fields.

        Example:
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
        """
        data = await self._http.get(f"/api/v1/hub-profiles/{hub_profile_id}")
        return GetHubProfile.model_validate(data)

    async def get_by_username(self, username: str) -> GetHubProfile:
        """
        Get a hub profile by its username.

        Retrieves the full details of a hub profile using its URL slug
        instead of its ID.

        Args:
            username: The hub profile's username / URL slug.

        Returns:
            GetHubProfile with all profile fields.

        Example:
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
        """
        data = await self._http.get(f"/api/v1/hub-profiles/username/{username}")
        return GetHubProfile.model_validate(data)

    async def list(self) -> builtins.list[MinimalHubProfile]:
        """
        List all hub profiles in the current workspace.

        Returns a minimal summary of each hub profile in the workspace
        associated with the client's API key.

        Returns:
            List of MinimalHubProfile objects.

        Example:
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
        """
        if not self._workspace_id:
            raw: builtins.list = await self._http.get("/api/v1/workspaces") or []
            if not raw:
                raise SRGError("No workspaces found for this API key")
            self._workspace_id = raw[0]["id"]
        data = await self._http.get(
            f"/api/v1/workspaces/{self._workspace_id}/hub-profiles"
        )
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    async def list_managed(self) -> builtins.list[MinimalHubProfile]:
        """
        List all hub profiles managed by the current user.

        Returns every hub profile for which the current API key user has
        an Admin or Editor role.

        Returns:
            List of MinimalHubProfile objects.

        Example:
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
        """
        data = await self._http.get("/api/v1/hub-profiles/managed")
        return [MinimalHubProfile.model_validate(item) for item in (data or [])]

    async def update(
        self,
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
        widgets: builtins.list[dict] | None = None,
    ) -> GetHubProfile | HubProfileSignedUrls:
        """
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

        Args:
            hub_profile_id: ID of the hub profile to update.
            name: New display name.
            user_name: New username / URL slug.
            sub_name: New subtitle. Pass ``None`` to clear.
            description: New description text. Pass ``None`` to clear.
            primary_url: New primary external URL. Pass ``None`` to clear.
            availability_level: New visibility — ``"Public"`` or ``"Private"``.
            app_clip_on: Whether to enable iOS App Clip.
            buttons: New list of action buttons. Replaces the existing list.
            avatar_image: Local path or ``http(s)://`` URL of the new avatar
                image. Triggers auto-upload.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            avatar: Avatar upload parameters (manual mode).
            cover: Cover upload parameters (manual mode).
            widgets: New widget configuration. Replaces the existing widgets.

        Returns:
            :class:`~srg.schemas.hub_profile.GetHubProfile` when
            ``avatar_image`` or ``cover_image`` is provided (auto-upload mode).
            :class:`~srg.schemas.hub_profile.HubProfileSignedUrls` otherwise
            (manual mode).

        Example:
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
        """
        if avatar_image is not None and avatar is None:
            avatar = FileUploadParameters(
                extension=extension_from_source(avatar_image),
                generate_signed_url=True,
            )
        if cover_image is not None and cover is None:
            cover = FileUploadParameters(
                extension=extension_from_source(cover_image),
                generate_signed_url=True,
            )

        body: dict = {
            "name": name,
            "userName": user_name,
            "availabilityLevel": _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            ),
            "appClipOn": app_clip_on,
            "buttons": [
                b.model_dump(by_alias=True, exclude_none=True) for b in (buttons or [])
            ],
        }
        if sub_name is not None:
            body["subName"] = sub_name
        if description is not None:
            body["description"] = description
        if primary_url is not None:
            body["primaryUrl"] = primary_url
        if avatar is not None:
            body["avatar"] = avatar.model_dump(by_alias=True, exclude_none=True)
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)
        if widgets is not None:
            body["widgets"] = widgets

        data = await self._http.put(f"/api/v1/hub-profiles/{hub_profile_id}", json=body)
        result = HubProfileSignedUrls.model_validate(data)

        if avatar_image is not None and result.avatar_signed_url is not None:
            await upload_to_signed_url_async(result.avatar_signed_url.url, avatar_image)
        if cover_image is not None and result.cover_signed_url is not None:
            await upload_to_signed_url_async(result.cover_signed_url.url, cover_image)

        if avatar_image is not None or cover_image is not None:
            return await self.get(hub_profile_id)
        return result

    async def archive(self, hub_profile_id: str) -> dict | None:
        """
        Archive a hub profile.

        Moves the hub profile to an archived state. Archived profiles are
        hidden from public listings but can be restored. Content within the
        profile is preserved.

        Args:
            hub_profile_id: ID of the hub profile to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.archive("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return await self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/archive")

    async def restore(self, hub_profile_id: str) -> dict | None:
        """
        Restore a previously archived hub profile.

        Makes the hub profile active again after it was archived.

        Args:
            hub_profile_id: ID of the hub profile to restore.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.restore("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return await self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/restore")

    async def delete(self, hub_profile_id: str) -> None:
        """
        Permanently delete a hub profile.

        Removes the hub profile and all of its data. This action is
        irreversible.

        Args:
            hub_profile_id: ID of the hub profile to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.delete("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        await self._http.delete(f"/api/v1/hub-profiles/{hub_profile_id}")

    async def join(self, hub_profile_id: str) -> dict | None:
        """
        Join a public hub profile as the current user.

        Registers the current API key user as a member of the hub profile.

        Args:
            hub_profile_id: ID of the hub profile to join.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.join("01965f7a-0000-7000-8000-000000000002")
        ```
        """
        return await self._http.post(f"/api/v1/hub-profiles/{hub_profile_id}/join")

    async def filter(
        self,
        *,
        ids: builtins.list[str],
        availability_level: AvailabilityLevel | None = None,
    ) -> builtins.list[HubProfileFilter]:
        """
        Get minimal info for a list of hub profile IDs.

        Batch-fetches lightweight hub profile data (ID, name, username,
        avatar) for a list of known IDs. Optionally filter to a specific
        visibility level.

        Args:
            ids: List of hub profile IDs to look up.
            availability_level: If provided, only returns profiles matching
                this visibility level (``"Public"`` or ``"Private"``).

        Returns:
            List of HubProfileFilter objects (minimal representation).

        Example:
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
        """
        body: dict = {"ids": ids}
        if availability_level is not None:
            body["availabilityLevel"] = _AVAILABILITY_LEVEL.get(
                availability_level, availability_level
            )
        data = await self._http.post("/api/v1/hub-profiles/filter", json=body)
        return [HubProfileFilter.model_validate(item) for item in (data or [])]

    async def move_to_workspace(
        self, hub_profile_id: str, workspace_id: str
    ) -> dict | None:
        """
        Move a hub profile to a different workspace.

        Transfers ownership of the hub profile to the specified workspace.

        Args:
            hub_profile_id: ID of the hub profile to move.
            workspace_id: ID of the destination workspace.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.move_to_workspace(
                "01965f7a-0000-7000-8000-000000000002",
                "01965f7a-0000-7000-8000-000000000050",
            )
        ```
        """
        return await self._http.post(
            f"/api/v1/hub-profiles/{hub_profile_id}/move-to/workspaces/{workspace_id}"
        )

    async def turn_on_community(self, hub_profile_id: str) -> dict | None:
        """
        Enable community features for a hub profile.

        Activates the community module for the hub profile, allowing members
        to interact through posts, comments, and reactions.

        Args:
            hub_profile_id: ID of the hub profile to enable community for.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.hub_profiles.turn_on_community(
                "01965f7a-0000-7000-8000-000000000002"
            )
        ```
        """
        return await self._http.post(
            f"/api/v1/hub-profiles/{hub_profile_id}/turn-on-community"
        )
