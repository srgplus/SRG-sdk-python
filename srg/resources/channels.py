import builtins
from collections.abc import AsyncIterator, Iterator

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.exceptions import SRGError
from srg.schemas.channel import (
    CategoryToReorder,
    CategoryWithHubProfile,
    Channel,
    ChannelCategoryOptionsUpsert,
    HubProfileChannelV2,
    OrderedContentToCategoryReference,
    SectionBaseCreate,
)
from srg.schemas.common import ChannelPrivacy, CursorPagedList


class ChannelsResource:
    def __init__(self, registry: dict[str, SyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> SyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    def create(
        self,
        *,
        name: str,
        hub_profile_id: str,
        privacy: ChannelPrivacy = "Private",
        workspace_id: str,
    ) -> str:
        """
        Create a new channel in a hub profile.

        Channels are the primary organizational unit inside a hub profile.
        They contain categories, which in turn contain sections and content.

        Args:
            name: Display name of the new channel.
            hub_profile_id: ID of the hub profile to create the channel in.
            privacy: Channel visibility — ``"Private"`` (default, only
                members can see it) or ``"Public"`` (visible to anyone).

        Returns:
            ID of the newly created channel.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channel_id = client.channels.create(
            name="Onboarding",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            privacy="Public",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000003"
        ```
        """
        data = self._get_http(workspace_id).post(
            "/api/v1/channels",
            json={
                "name": name,
                "hubProfileId": hub_profile_id,
                "privacy": privacy,
            },
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    def list(
        self,
        hub_profile_id: str,
        *,
        include_archived: bool = False,
        workspace_id: str,
    ) -> list[Channel]:
        """
        List all channels for a hub profile.

        Returns every channel in the hub profile, along with their
        categories. Archived channels are excluded by default.

        Args:
            hub_profile_id: ID of the hub profile.
            include_archived: If True, include archived channels in the
                result. Defaults to False.

        Returns:
            List of Channel objects.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channels = client.channels.list(
            "01965f7a-0000-7000-8000-000000000002",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        [
            Channel(
                id="01965f7a-0000-7000-8000-000000000003",
                name="Onboarding",
                categories=[
                    Category(
                        id="01965f7a-0000-7000-8000-000000000004",
                        name="Week 1",
                        is_archived=False,
                        is_pinned=False,
                        notifications_enabled=True,
                        sections=[],
                        options=None,
                    ),
                ],
            ),
        ]
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v1/channels/{hub_profile_id}",
            params={"includeArchived": str(include_archived).lower()},
        )
        return [Channel.model_validate(item) for item in (data or [])]

    def get(self, channel_id: str, *, workspace_id: str) -> HubProfileChannelV2:
        """
        Get detailed channel data by ID (v2).

        Retrieves the full channel details using the v2 schema, which includes
        categories with their heading content (a preview of pinned content
        items at the top of each category).

        Args:
            channel_id: ID of the channel to retrieve.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channel = client.channels.get(
            "01965f7a-0000-7000-8000-000000000003",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[
                CategoryWithHeadingContent(
                    id="01965f7a-0000-7000-8000-000000000004",
                    name="Week 1",
                    is_archived=False,
                    is_pinned=False,
                    notifications_enabled=True,
                    sections=[],
                    options=None,
                    heading_content=CategoryHeadingContent(
                        references=[],
                        total_count=0,
                        next_cursor=None,
                        has_next=False,
                    ),
                ),
            ],
        )
        ```
        """
        data = self._get_http(workspace_id).get(f"/api/v2/channels/{channel_id}")
        return HubProfileChannelV2.model_validate(data)

    def get_by_name(
        self,
        hub_profile_username: str,
        channel_name: str,
        workspace_id: str,
    ) -> HubProfileChannelV2:
        """
        Get detailed channel data by hub profile username and channel name (v2).

        Retrieves a channel using human-readable slugs instead of IDs. Useful
        for public-facing integrations where you only know the profile and
        channel names.

        Args:
            hub_profile_username: Username / slug of the hub profile (e.g.
                ``"acme-academy"``).
            channel_name: Name slug of the channel (e.g. ``"onboarding"``).

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channel = client.channels.get_by_name(
            "acme-academy",
            "onboarding",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}"
        )
        return HubProfileChannelV2.model_validate(data)

    def update(
        self,
        *,
        channel_id: str,
        hub_profile_id: str,
        name: str,
        privacy: ChannelPrivacy | None = None,
        categories: builtins.list[CategoryToReorder] | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update a channel's name, privacy, and category order.

        Replaces the channel's name and optionally updates its privacy
        setting and category ordering. All provided fields are overwritten.

        Args:
            channel_id: ID of the channel to update.
            hub_profile_id: ID of the hub profile the channel belongs to.
            name: New display name for the channel.
            privacy: New privacy setting. Unchanged if not provided.
            categories: New category ordering. Each entry specifies a category
                ID and its new ``order`` index. Unchanged if not provided.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        from sdk.schemas.channel import CategoryToReorder

        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.update(
            channel_id="01965f7a-0000-7000-8000-000000000003",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            name="Onboarding (Updated)",
            privacy="Public",
            categories=[
                CategoryToReorder(id="01965f7a-0000-7000-8000-000000000004", order=0),
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body: dict = {
            "channelId": channel_id,
            "hubProfileId": hub_profile_id,
            "name": name,
            "categories": [
                c.model_dump(by_alias=True, exclude_none=True)
                for c in (categories or [])
            ],
        }
        if privacy is not None:
            body["privacy"] = privacy
        return self._get_http(workspace_id).put("/api/v1/channels", json=body)

    def archive(self, channel_id: str, *, workspace_id: str) -> dict | None:
        """
        Archive a channel.

        Moves the channel to an archived state. Its content is preserved
        but the channel is hidden from members.

        Args:
            channel_id: ID of the channel to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.archive(
            "01965f7a-0000-7000-8000-000000000003",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/archive"
        )

    def restore(self, channel_id: str, *, workspace_id: str) -> dict | None:
        """Restore a previously archived channel."""
        return self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/restore"
        )

    def delete(self, channel_id: str, *, workspace_id: str) -> None:
        """
        Permanently delete a channel.

        Removes the channel and all of its categories, sections, and content
        references. This action is irreversible.

        Args:
            channel_id: ID of the channel to delete.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.delete(
            "01965f7a-0000-7000-8000-000000000003",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(f"/api/v1/channels/{channel_id}")

    def create_category(
        self,
        channel_id: str,
        *,
        name: str,
        is_pinned: bool = False,
        notifications_enabled: bool = True,
        options: ChannelCategoryOptionsUpsert | None = None,
        sections: builtins.list[SectionBaseCreate] | None = None,
        workspace_id: str,
    ) -> str:
        """
        Create a new category inside a channel.

        Categories group content within a channel. Optionally, initial
        sections and display options can be provided at creation time.

        Args:
            channel_id: ID of the channel to add the category to.
            name: Display name of the new category.
            is_pinned: Whether to pin the category to the top of the
                channel. Defaults to False.
            notifications_enabled: Whether to send notifications for new
                content in this category. Defaults to True.
            options: Display and behaviour options (view type, progression
                tracking, cover visibility, expandable). If omitted, defaults
                are used.
            sections: Initial sections to create inside the category.

        Returns:
            ID of the newly created category.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        category_id = client.channels.create_category(
            "01965f7a-0000-7000-8000-000000000003",
            name="Week 1",
            is_pinned=True,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000004"
        ```
        """
        body: dict = {
            "name": name,
            "isPinned": is_pinned,
            "notificationsEnabled": notifications_enabled,
            "options": (options or ChannelCategoryOptionsUpsert()).model_dump(
                by_alias=True, exclude_none=True
            ),
            "sections": [
                s.model_dump(by_alias=True, exclude_none=True) for s in (sections or [])
            ],
        }
        data = self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/categories", json=body
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    def update_category(
        self,
        channel_id: str,
        category_id: str,
        *,
        name: str,
        is_pinned: bool = False,
        notifications_enabled: bool = True,
        options: ChannelCategoryOptionsUpsert | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update a category's name, pin status, notifications, and display options.

        Replaces all category settings with the provided values. All fields
        are overwritten.

        Args:
            channel_id: ID of the channel the category belongs to.
            category_id: ID of the category to update.
            name: New display name.
            is_pinned: Whether to pin the category. Defaults to False.
            notifications_enabled: Whether notifications are enabled. Defaults
                to True.
            options: Updated display and behaviour options.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.update_category(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            name="Week 1 (Updated)",
            is_pinned=False,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body: dict = {
            "name": name,
            "isPinned": is_pinned,
            "notificationsEnabled": notifications_enabled,
            "options": (options or ChannelCategoryOptionsUpsert()).model_dump(
                by_alias=True, exclude_none=True
            ),
        }
        return self._get_http(workspace_id).put(
            f"/api/v1/channels/{channel_id}/categories/{category_id}",
            json=body,
        )

    def archive_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> dict | None:
        """
        Archive a category.

        Moves the category to an archived state. Content references within
        the category are preserved but it is hidden from members.

        Args:
            channel_id: ID of the channel the category belongs to.
            category_id: ID of the category to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.archive_category(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/archive"
        )

    def restore_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> dict | None:
        """Restore a previously archived category."""
        return self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/restore"
        )

    def delete_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> None:
        """
        Permanently delete a category from a channel.

        Removes the category and all of its sections and content references.
        This action is irreversible.

        Args:
            channel_id: ID of the channel the category belongs to.
            category_id: ID of the category to delete.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.delete_category(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/channels/{channel_id}/{category_id}"
        )

    def get_category_references(
        self,
        channel_id: str,
        category_id: str,
        *,
        page_size: int = 20,
        cursor: str | None = None,
        workspace_id: str,
    ) -> CursorPagedList[OrderedContentToCategoryReference]:
        """
        List content references in a category with cursor-based pagination.

        Returns a page of ordered content-to-category reference objects,
        each identifying a content item placed in this category and its
        position within the category.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            page_size: Maximum number of references to return per page.
                Defaults to 20.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.

        Returns:
            CursorPagedList[OrderedContentToCategoryReference] with content
            references and an optional cursor for the next page.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        page = client.channels.get_category_references(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            page_size=10,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                OrderedContentToCategoryReference(
                    content_id="01965f7a-0000-7000-8000-000000000005",
                    section_id="01965f7a-0000-7000-8000-000000000011",
                    order=0,
                ),
                OrderedContentToCategoryReference(
                    content_id="01965f7a-0000-7000-8000-000000000012",
                    section_id="01965f7a-0000-7000-8000-000000000011",
                    order=1,
                ),
            ],
            cursor=None,
        )
        ```
        """
        params: dict = {"pageSize": page_size}
        if cursor:
            params["cursor"] = cursor
        data = self._get_http(workspace_id).get(
            f"/api/v1/channels/{channel_id}/{category_id}/references",
            params=params,
        )
        items = [
            OrderedContentToCategoryReference.model_validate(i)
            for i in (data.get("items") or [])
        ]
        return CursorPagedList[OrderedContentToCategoryReference](
            items=items,
            cursor=data.get("cursor"),
        )

    def get_category_references_all(
        self,
        channel_id: str,
        category_id: str,
        *,
        page_size: int = 50,
        workspace_id: str,
    ) -> Iterator[OrderedContentToCategoryReference]:
        """
        Iterate over all content references in a category across all pages.

        Wraps :meth:`get_category_references` and handles cursor-based
        pagination automatically. Yields individual
        :class:`~srg.schemas.channel.OrderedContentToCategoryReference` items.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            page_size: Items per page. Defaults to 50.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        for ref in client.channels.get_category_references_all(
            channel_id,
            category_id,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        ):
            print(ref.content_id, ref.order)
        ```
        """
        cursor: str | None = None
        while True:
            page = self.get_category_references(
                channel_id,
                category_id,
                page_size=page_size,
                cursor=cursor,
                workspace_id=workspace_id,
            )
            yield from page.items
            cursor = page.cursor
            if cursor is None:
                break

    def create_section(
        self, channel_id: str, category_id: str, *, name: str, workspace_id: str
    ) -> str:
        """
        Create a new section inside a channel category.

        Sections subdivide a category into named groups of content. Content
        items are placed into a section when added to a category.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category to add the section to.
            name: Display name of the new section.

        Returns:
            ID of the newly created section.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        section_id = client.channels.create_section(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            name="Videos",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000011"
        ```
        """
        data = self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/sections",
            json={"name": name},
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    def update_section(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        *,
        name: str,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the name of a section.

        Renames the section. Does not affect the content items it contains.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category containing the section.
            section_id: ID of the section to update.
            name: New display name for the section.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.update_section(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            "01965f7a-0000-7000-8000-000000000011",
            name="Training Videos",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).put(
            f"/api/v1/channels/{channel_id}/{category_id}/sections/{section_id}",
            json={"name": name},
        )

    def delete_section(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        workspace_id: str,
    ) -> None:
        """
        Permanently delete a section from a channel category.

        Removes the section and all content references within it. This
        action is irreversible.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category containing the section.
            section_id: ID of the section to delete.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.delete_section(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            "01965f7a-0000-7000-8000-000000000011",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/channels/{channel_id}/{category_id}/sections/{section_id}"
        )

    def add_content_to_category(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        *,
        contents_ids: builtins.list[str],
        workspace_id: str,
    ) -> dict | None:
        """
        Add content items to a category section.

        Places one or more content items into the specified section of a
        channel category. Duplicate additions are ignored.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            section_id: ID of the section within the category.
            contents_ids: List of content IDs to add.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.channels.add_content_to_category(
            "01965f7a-0000-7000-8000-000000000003",
            "01965f7a-0000-7000-8000-000000000004",
            "01965f7a-0000-7000-8000-000000000011",
            contents_ids=[
                "01965f7a-0000-7000-8000-000000000005",
                "01965f7a-0000-7000-8000-000000000012",
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/{section_id}/content",
            json={"contentsIds": contents_ids},
        )

    def get_v2(self, channel_id: str, *, workspace_id: str) -> HubProfileChannelV2:
        """
        Get detailed channel data by ID (v2).

        Alias for ``get``. Retrieves the full channel details using the v2
        schema, including categories with heading content.

        Args:
            channel_id: ID of the channel to retrieve.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channel = client.channels.get_v2(
            "01965f7a-0000-7000-8000-000000000003",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = self._get_http(workspace_id).get(f"/api/v2/channels/{channel_id}")
        return HubProfileChannelV2.model_validate(data)

    def get_by_name_v2(
        self,
        hub_profile_username: str,
        channel_name: str,
        workspace_id: str,
    ) -> HubProfileChannelV2:
        """
        Get detailed channel data by hub profile username and channel name (v2).

        Alias for ``get_by_name``. Retrieves a channel using human-readable
        slugs instead of IDs.

        Args:
            hub_profile_username: Username / slug of the hub profile.
            channel_name: Name slug of the channel.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        channel = client.channels.get_by_name_v2(
            "acme-academy",
            "onboarding",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}"
        )
        return HubProfileChannelV2.model_validate(data)

    def get_category_v2(
        self,
        hub_profile_username: str,
        channel_name: str,
        category_name: str,
        workspace_id: str,
    ) -> CategoryWithHubProfile:
        """
        Get category details by hub profile username, channel name, and category name (v2).

        Retrieves a specific category using human-readable slugs for the hub
        profile, channel, and category. The response includes the hub profile
        context alongside the category data and its heading content.

        Args:
            hub_profile_username: Username / slug of the hub profile.
            channel_name: Name slug of the channel.
            category_name: Name slug of the category.

        Returns:
            CategoryWithHubProfile containing category details and the
            associated hub profile context.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        category = client.channels.get_category_v2(
            "acme-academy",
            "onboarding",
            "week-1",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        CategoryWithHubProfile(
            id="01965f7a-0000-7000-8000-000000000004",
            name="Week 1",
            is_archived=False,
            is_pinned=False,
            notifications_enabled=True,
            heading_content=CategoryHeadingContent(
                references=[],
                total_count=0,
                next_cursor=None,
                has_next=False,
            ),
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
        )
        ```
        """
        data = self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}/categories/{category_name}"
        )
        return CategoryWithHubProfile.model_validate(data)


class AsyncChannelsResource:
    def __init__(self, registry: dict[str, AsyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> AsyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    async def create(
        self,
        *,
        name: str,
        hub_profile_id: str,
        privacy: str = "Private",
        workspace_id: str,
    ) -> str:
        """
        Create a new channel in a hub profile.

        Channels are the primary organizational unit inside a hub profile.
        They contain categories, which in turn contain sections and content.

        Args:
            name: Display name of the new channel.
            hub_profile_id: ID of the hub profile to create the channel in.
            privacy: Channel visibility — ``"Private"`` (default) or
                ``"Public"``.

        Returns:
            ID of the newly created channel.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channel_id = await client.channels.create(
                name="Onboarding",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                privacy="Public",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000003"
        ```
        """
        data = await self._get_http(workspace_id).post(
            "/api/v1/channels",
            json={
                "name": name,
                "hubProfileId": hub_profile_id,
                "privacy": privacy,
            },
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    async def list(
        self,
        hub_profile_id: str,
        *,
        include_archived: bool = False,
        workspace_id: str,
    ) -> list[Channel]:
        """
        List all channels for a hub profile.

        Returns every channel in the hub profile along with their categories.
        Archived channels are excluded by default.

        Args:
            hub_profile_id: ID of the hub profile.
            include_archived: If True, include archived channels. Defaults to
                False.

        Returns:
            List of Channel objects.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channels = await client.channels.list(
                "01965f7a-0000-7000-8000-000000000002",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        [
            Channel(
                id="01965f7a-0000-7000-8000-000000000003",
                name="Onboarding",
                categories=[],
            ),
        ]
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v1/channels/{hub_profile_id}",
            params={"includeArchived": str(include_archived).lower()},
        )
        return [Channel.model_validate(item) for item in (data or [])]

    async def get(self, channel_id: str, *, workspace_id: str) -> HubProfileChannelV2:
        """
        Get detailed channel data by ID (v2).

        Retrieves the full channel details using the v2 schema, which includes
        categories with their heading content.

        Args:
            channel_id: ID of the channel to retrieve.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channel = await client.channels.get(
                "01965f7a-0000-7000-8000-000000000003",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = await self._get_http(workspace_id).get(f"/api/v2/channels/{channel_id}")
        return HubProfileChannelV2.model_validate(data)

    async def get_by_name(
        self,
        hub_profile_username: str,
        channel_name: str,
        workspace_id: str,
    ) -> HubProfileChannelV2:
        """
        Get detailed channel data by hub profile username and channel name (v2).

        Args:
            hub_profile_username: Username / slug of the hub profile.
            channel_name: Name slug of the channel.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channel = await client.channels.get_by_name(
                "acme-academy",
                "onboarding",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}"
        )
        return HubProfileChannelV2.model_validate(data)

    async def update(
        self,
        *,
        channel_id: str,
        hub_profile_id: str,
        name: str,
        privacy: ChannelPrivacy | None = None,
        categories: builtins.list[CategoryToReorder] | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update a channel's name, privacy, and category order.

        Replaces the channel's name and optionally its privacy setting and
        category ordering.

        Args:
            channel_id: ID of the channel to update.
            hub_profile_id: ID of the hub profile the channel belongs to.
            name: New display name for the channel.
            privacy: New privacy setting. Unchanged if not provided.
            categories: New category ordering. Unchanged if not provided.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.update(
                channel_id="01965f7a-0000-7000-8000-000000000003",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                name="Onboarding (Updated)",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body: dict = {
            "channelId": channel_id,
            "hubProfileId": hub_profile_id,
            "name": name,
            "categories": [
                c.model_dump(by_alias=True, exclude_none=True)
                for c in (categories or [])
            ],
        }
        if privacy is not None:
            body["privacy"] = privacy
        return await self._get_http(workspace_id).put("/api/v1/channels", json=body)

    async def archive(self, channel_id: str, *, workspace_id: str) -> dict | None:
        """
        Archive a channel.

        Moves the channel to an archived state.

        Args:
            channel_id: ID of the channel to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.archive(
                "01965f7a-0000-7000-8000-000000000003",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/archive"
        )

    async def restore(self, channel_id: str, *, workspace_id: str) -> dict | None:
        """Restore a previously archived channel."""
        return await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/restore"
        )

    async def delete(self, channel_id: str, *, workspace_id: str) -> None:
        """
        Permanently delete a channel.

        Removes the channel and all of its categories, sections, and content
        references. This action is irreversible.

        Args:
            channel_id: ID of the channel to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.delete(
                "01965f7a-0000-7000-8000-000000000003",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(f"/api/v1/channels/{channel_id}")

    async def create_category(
        self,
        channel_id: str,
        *,
        name: str,
        is_pinned: bool = False,
        notifications_enabled: bool = True,
        options: ChannelCategoryOptionsUpsert | None = None,
        sections: builtins.list[SectionBaseCreate] | None = None,
        workspace_id: str,
    ) -> str:
        """
        Create a new category inside a channel.

        Args:
            channel_id: ID of the channel to add the category to.
            name: Display name of the new category.
            is_pinned: Whether to pin the category. Defaults to False.
            notifications_enabled: Whether to send notifications for new
                content. Defaults to True.
            options: Display and behaviour options.
            sections: Initial sections to create inside the category.

        Returns:
            ID of the newly created category.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            category_id = await client.channels.create_category(
                "01965f7a-0000-7000-8000-000000000003",
                name="Week 1",
                is_pinned=True,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000004"
        ```
        """
        body: dict = {
            "name": name,
            "isPinned": is_pinned,
            "notificationsEnabled": notifications_enabled,
            "options": (options or ChannelCategoryOptionsUpsert()).model_dump(
                by_alias=True, exclude_none=True
            ),
            "sections": [
                s.model_dump(by_alias=True, exclude_none=True) for s in (sections or [])
            ],
        }

        data = await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/categories", json=body
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    async def update_category(
        self,
        channel_id: str,
        category_id: str,
        *,
        name: str,
        is_pinned: bool = False,
        notifications_enabled: bool = True,
        options: ChannelCategoryOptionsUpsert | None = None,
        workspace_id: str,
    ) -> dict | None:
        """
        Update a category's name, pin status, notifications, and display options.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category to update.
            name: New display name.
            is_pinned: Whether to pin the category. Defaults to False.
            notifications_enabled: Whether notifications are enabled.
                Defaults to True.
            options: Updated display and behaviour options.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.update_category(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                name="Week 1 (Updated)",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body: dict = {
            "name": name,
            "isPinned": is_pinned,
            "notificationsEnabled": notifications_enabled,
            "options": (options or ChannelCategoryOptionsUpsert()).model_dump(
                by_alias=True, exclude_none=True
            ),
        }
        return await self._get_http(workspace_id).put(
            f"/api/v1/channels/{channel_id}/categories/{category_id}",
            json=body,
        )

    async def archive_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> dict | None:
        """
        Archive a category.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category to archive.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.archive_category(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/archive"
        )

    async def restore_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> dict | None:
        """Restore a previously archived category."""
        return await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/restore"
        )

    async def delete_category(
        self, channel_id: str, category_id: str, *, workspace_id: str
    ) -> None:
        """
        Permanently delete a category from a channel.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.delete_category(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/channels/{channel_id}/{category_id}"
        )

    async def get_category_references(
        self,
        channel_id: str,
        category_id: str,
        *,
        page_size: int = 20,
        cursor: str | None = None,
        workspace_id: str,
    ) -> CursorPagedList[OrderedContentToCategoryReference]:
        """
        List content references in a category with cursor-based pagination.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            page_size: Maximum number of references per page. Defaults to 20.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.

        Returns:
            CursorPagedList[OrderedContentToCategoryReference].

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            page = await client.channels.get_category_references(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                OrderedContentToCategoryReference(
                    content_id="01965f7a-0000-7000-8000-000000000005",
                    section_id="01965f7a-0000-7000-8000-000000000011",
                    order=0,
                ),
            ],
            cursor=None,
        )
        ```
        """
        params: dict = {"pageSize": page_size}
        if cursor:
            params["cursor"] = cursor
        data = await self._get_http(workspace_id).get(
            f"/api/v1/channels/{channel_id}/{category_id}/references",
            params=params,
        )
        items = [
            OrderedContentToCategoryReference.model_validate(i)
            for i in (data.get("items") or [])
        ]
        return CursorPagedList[OrderedContentToCategoryReference](
            items=items,
            cursor=data.get("cursor"),
        )

    async def get_category_references_all(
        self,
        channel_id: str,
        category_id: str,
        *,
        page_size: int = 50,
        workspace_id: str,
    ) -> AsyncIterator[OrderedContentToCategoryReference]:
        """
        Async-iterate over all content references in a category across all pages.

        Wraps :meth:`get_category_references` and handles cursor-based
        pagination automatically.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            async for ref in client.channels.get_category_references_all(
                channel_id,
                category_id,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            ):
                print(ref.content_id, ref.order)
        ```
        """
        cursor: str | None = None
        while True:
            page = await self.get_category_references(
                channel_id,
                category_id,
                page_size=page_size,
                cursor=cursor,
                workspace_id=workspace_id,
            )
            for item in page.items:
                yield item
            cursor = page.cursor
            if cursor is None:
                break

    async def create_section(
        self,
        channel_id: str,
        category_id: str,
        *,
        name: str,
        workspace_id: str,
    ) -> str:
        """
        Create a new section inside a channel category.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            name: Display name of the new section.

        Returns:
            ID of the newly created section.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            section_id = await client.channels.create_section(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                name="Videos",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        "01965f7a-0000-7000-8000-000000000011"
        ```
        """
        data = await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/sections",
            json={"name": name},
        )
        if isinstance(data, dict):
            return data.get("id", "")
        return str(data or "")

    async def update_section(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        *,
        name: str,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the name of a section.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            section_id: ID of the section to update.
            name: New display name.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.update_section(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                "01965f7a-0000-7000-8000-000000000011",
                name="Training Videos",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).put(
            f"/api/v1/channels/{channel_id}/{category_id}/sections/{section_id}",
            json={"name": name},
        )

    async def delete_section(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        workspace_id: str,
    ) -> None:
        """
        Permanently delete a section from a channel category.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            section_id: ID of the section to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.delete_section(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                "01965f7a-0000-7000-8000-000000000011",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/channels/{channel_id}/{category_id}/sections/{section_id}"
        )

    async def add_content_to_category(
        self,
        channel_id: str,
        category_id: str,
        section_id: str,
        *,
        contents_ids: builtins.list[str],
        workspace_id: str,
    ) -> dict | None:
        """
        Add content items to a category section.

        Args:
            channel_id: ID of the channel.
            category_id: ID of the category.
            section_id: ID of the section.
            contents_ids: List of content IDs to add.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.channels.add_content_to_category(
                "01965f7a-0000-7000-8000-000000000003",
                "01965f7a-0000-7000-8000-000000000004",
                "01965f7a-0000-7000-8000-000000000011",
                contents_ids=["01965f7a-0000-7000-8000-000000000005"],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).post(
            f"/api/v1/channels/{channel_id}/{category_id}/{section_id}/content",
            json={"contentsIds": contents_ids},
        )

    async def get_v2(
        self, channel_id: str, *, workspace_id: str
    ) -> HubProfileChannelV2:
        """
        Get detailed channel data by ID (v2).

        Args:
            channel_id: ID of the channel to retrieve.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channel = await client.channels.get_v2(
                "01965f7a-0000-7000-8000-000000000003",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = await self._get_http(workspace_id).get(f"/api/v2/channels/{channel_id}")
        return HubProfileChannelV2.model_validate(data)

    async def get_by_name_v2(
        self,
        hub_profile_username: str,
        channel_name: str,
        workspace_id: str,
    ) -> HubProfileChannelV2:
        """
        Get detailed channel data by hub profile username and channel name (v2).

        Args:
            hub_profile_username: Username / slug of the hub profile.
            channel_name: Name slug of the channel.

        Returns:
            HubProfileChannelV2 with categories and heading content.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            channel = await client.channels.get_by_name_v2(
                "acme-academy",
                "onboarding",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        HubProfileChannelV2(
            id="01965f7a-0000-7000-8000-000000000003",
            name="Onboarding",
            privacy="Public",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
            categories=[],
        )
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}"
        )
        return HubProfileChannelV2.model_validate(data)

    async def get_category_v2(
        self,
        hub_profile_username: str,
        channel_name: str,
        category_name: str,
        workspace_id: str,
    ) -> CategoryWithHubProfile:
        """
        Get category details by hub profile username, channel name, and category name (v2).

        Args:
            hub_profile_username: Username / slug of the hub profile.
            channel_name: Name slug of the channel.
            category_name: Name slug of the category.

        Returns:
            CategoryWithHubProfile containing category details and hub
            profile context.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            category = await client.channels.get_category_v2(
                "acme-academy",
                "onboarding",
                "week-1",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        CategoryWithHubProfile(
            id="01965f7a-0000-7000-8000-000000000004",
            name="Week 1",
            is_archived=False,
            is_pinned=False,
            notifications_enabled=True,
            heading_content=CategoryHeadingContent(
                references=[],
                total_count=0,
                next_cursor=None,
                has_next=False,
            ),
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            hub_profile_user_name="acme-academy",
        )
        ```
        """
        data = await self._get_http(workspace_id).get(
            f"/api/v2/channels/{hub_profile_username}/{channel_name}/categories/{category_name}"
        )
        return CategoryWithHubProfile.model_validate(data)
