from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg._upload import (
    extension_from_source,
    put_bytes_to_signed_url,
    put_bytes_to_signed_url_async,
    read_image_async,
    read_image_sync,
)
from srg.schemas.common import (
    ContentFileUploadParameters,
    ContentPrivacy,
    CursorPagedList,
    ImageUpsert,
    ProgressionStatus,
)
from srg.schemas.content import (
    CollectionProgressionStats,
    Content,
    ContentChannelUpsert,
    ContentProgression,
    ContentSearch,
    ContentUploadSignedUrl,
    ContentV2,
)


def _ser_list(items: list[Any]) -> list[Any]:
    return [
        v.model_dump(by_alias=True, exclude_none=True)
        if isinstance(v, BaseModel)
        else v
        for v in items
    ]


def _normalize_channels(
    channels: list[Any] | None,
) -> list[Any]:
    """Accept plain channel ID strings or full ContentChannelUpsert objects."""
    result = []
    for item in channels or []:
        if isinstance(item, str):
            result.append({"channelId": item, "categoryIds": []})
        elif isinstance(item, BaseModel):
            result.append(item.model_dump(by_alias=True, exclude_none=True))
        else:
            result.append(item)
    return result


def _make_image_upsert(img_bytes: bytes, source: str | Path) -> ImageUpsert:
    ext = extension_from_source(source)
    return ImageUpsert(width=1, height=1, size=len(img_bytes), extension=ext)


def _make_content_file_params(
    img_bytes: bytes, source: str | Path
) -> ContentFileUploadParameters:
    return ContentFileUploadParameters(
        image=_make_image_upsert(img_bytes, source),
        generate_signed_url=True,
    )


def _upload_cover_sync(
    result: ContentUploadSignedUrl,
    img_bytes: bytes,
    content_type: str,
) -> None:
    if result.cover_signed_url is not None:
        put_bytes_to_signed_url(
            result.cover_signed_url.url,
            img_bytes,
            content_type,
            extra_headers=result.metadata_headers,
        )


async def _upload_cover_async(
    result: ContentUploadSignedUrl,
    img_bytes: bytes,
    content_type: str,
) -> None:
    if result.cover_signed_url is not None:
        await put_bytes_to_signed_url_async(
            result.cover_signed_url.url,
            img_bytes,
            content_type,
            extra_headers=result.metadata_headers,
        )


class ContentsResource:
    def __init__(self, http: SyncHTTPClient) -> None:
        self._http = http

    def create(
        self,
        *,
        name: str,
        hub_profile_id: str,
        privacy: ContentPrivacy = "Preview",
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: Any | None = None,
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
    ) -> Content | ContentUploadSignedUrl:
        """
        Create a new content item in a hub profile.

        Creates a content item or collection inside the given hub profile and
        places it in the specified channels and categories.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image and returns the fully
        populated :class:`~srg.schemas.content.Content`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
        signed URL so you can upload the image yourself.

        Args:
            name: Display title of the content item.
            hub_profile_id: ID of the hub profile to create the content in.
            privacy: Visibility — ``"Preview"`` (default), ``"Private"``, or
                ``"Public"``.
            details: Optional body text / description.
            url: Optional external URL to associate with the content.
            main_asset_id: ID of the primary playable asset.
            cover_image: Local path or ``http(s)://`` URL of the cover image.
                Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            channels: Channel and category placements for this content.
            context: Additional context objects.
            categories: Category assignments.

        Returns:
            :class:`~srg.schemas.content.Content` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        from sdk.schemas.content import ContentChannelUpsert

        client = SRGClient(api_key="srgplus_your_key")
        content = client.contents.create(
            name="Welcome to the Team",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            privacy="Public",
            details="Everything you need to know for your first week.",
            main_asset_id="01965f7a-0000-7000-8000-000000000006",
            cover_image="/path/to/cover.jpg",
        )
        # content is Content with cover already populated
        ```

        Example response:
        ```python
        Content(
            id="01965f7a-0000-7000-8000-000000000005",
            name="Welcome to the Team",
            details="Everything you need to know for your first week.",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            cover=ContentCover(
                urls=CoverUrls(
                    original="https://cdn.srgplus.com/covers/welcome.jpg",
                ),
                extension="jpg",
                modified="2025-06-01T10:00:00Z",
            ),
            channels=[],
        )
        ```
        """
        # For create, `cover` in the API contract is `ImageUpsert` (not
        # ContentFileUploadParameters). We must include size so the server can
        # generate a signed URL with the correct content-length.
        _img_bytes: bytes | None = None
        _img_content_type: str | None = None

        if cover_image is not None and cover is None:
            _img_bytes, _img_content_type = read_image_sync(cover_image)
            cover = _make_image_upsert(_img_bytes, cover_image)

        body: dict = {
            "name": name,
            "hubProfileId": hub_profile_id,
            "privacy": privacy,
            "channels": _normalize_channels(channels),
            "context": _ser_list(context or []),
            "categories": _ser_list(categories or []),
        }
        if details is not None:
            body["details"] = details
        if url is not None:
            body["url"] = url
        if main_asset_id is not None:
            body["mainAssetId"] = main_asset_id
        if cover is not None:
            body["cover"] = (
                cover.model_dump(by_alias=True, exclude_none=True)
                if isinstance(cover, BaseModel)
                else cover
            )
        data = self._http.post("/api/v1/contents", json=body)
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            _upload_cover_sync(
                result, _img_bytes, _img_content_type or "application/octet-stream"
            )

        if cover_image is not None:
            return self.get(result.id, hub_profile_id=hub_profile_id)
        return result

    def get(self, content_id: str, *, hub_profile_id: str | None = None) -> Content:
        """
        Get a content item by ID (v1).

        Retrieves the full metadata for a content item, including its name,
        description, cover, channel placements, and creation timestamps.

        Use ``get_v2`` to also include the main playable asset and the
        current user's progression.

        Args:
            content_id: ID of the content item to retrieve.
            hub_profile_id: If provided, used to resolve access context for
                the request.

        Returns:
            Content object with metadata and channel placement details.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        content = client.contents.get("01965f7a-0000-7000-8000-000000000005")
        ```

        Example response:
        ```python
        Content(
            id="01965f7a-0000-7000-8000-000000000005",
            name="Welcome to the Team",
            details="Everything you need to know for your first week.",
            url=None,
            created_by="01965f7a-0000-7000-8000-000000000007",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            created="2025-06-01T10:00:00Z",
            archived=None,
            cover=ContentCover(
                urls=CoverUrls(
                    original="https://cdn.srgplus.com/covers/welcome.jpg",
                    thumbnail_large=None,
                    thumbnail_small=None,
                    large=None,
                    blurred_large=None,
                    seo=None,
                ),
                extension="jpg",
                modified="2025-06-01T10:00:00Z",
            ),
            channels=[
                ContentChannel(
                    id="01965f7a-0000-7000-8000-000000000003",
                    name="Onboarding",
                    categories=[
                        ContentChannelCategory(
                            id="01965f7a-0000-7000-8000-000000000004",
                            name="Week 1",
                        )
                    ],
                )
            ],
            heading_referenced_content=[],
        )
        ```
        """
        params = {"hubProfileId": hub_profile_id} if hub_profile_id else None
        data = self._http.get(f"/api/v1/contents/{content_id}", params=params)
        return Content.model_validate(data)

    def update(
        self,
        content_id: str,
        *,
        name: str | None = None,
        hub_profile_id: str | None = None,
        privacy: ContentPrivacy | None = None,
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: ContentFileUploadParameters | None = None,
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
    ) -> Content | ContentUploadSignedUrl:
        """
        Update a content item's metadata.

        Fetches the current state first, then merges the provided values.
        Fields left as ``None`` are preserved from the existing content —
        only explicitly passed values are changed.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or
        an ``http(s)://`` URL. The SDK uploads the image and returns the
        updated :class:`~srg.schemas.content.Content`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
        signed URL so you can upload the image yourself.

        Args:
            content_id: ID of the content item to update.
            name: New display title. Keeps existing if ``None``.
            hub_profile_id: Hub profile that owns this content.
            privacy: New visibility level. Keeps existing if ``None``.
            details: New body text. Keeps existing if ``None``.
            url: New external URL. Keeps existing if ``None``.
            main_asset_id: New primary asset ID. Keeps existing if ``None``.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            channels: Channel/category placements. Keeps existing if ``None``.
            context: Context widgets. Keeps existing if ``None``.
            categories: Category assignments. Keeps existing if ``None``.

        Returns:
            :class:`~srg.schemas.content.Content` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        # Only name and privacy change; channels/context/categories are preserved.
        content = client.contents.update(
            "01965f7a-0000-7000-8000-000000000005",
            name="Welcome to the Team (v2)",
            privacy="Public",
        )
        ```
        """
        existing = self.get_v2(content_id)

        _name = name if name is not None else existing.name
        _privacy = privacy if privacy is not None else existing.privacy
        _details = details if details is not None else existing.details
        _url = url if url is not None else existing.url
        _main_asset_id = (
            main_asset_id
            if main_asset_id is not None
            else (existing.main_asset.id if existing.main_asset else None)
        )
        _channels: list[str | ContentChannelUpsert] = (
            channels
            if channels is not None
            else [
                ContentChannelUpsert(
                    channel_id=ch.id,
                    category_ids=[c.id for c in ch.categories],
                )
                for ch in existing.channels
            ]
        )
        _context = context if context is not None else existing.context
        _categories = categories if categories is not None else existing.categories

        _img_bytes: bytes | None = None
        _img_content_type: str | None = None

        if cover_image is not None and cover is None:
            _img_bytes, _img_content_type = read_image_sync(cover_image)
            cover = _make_content_file_params(_img_bytes, cover_image)

        body: dict = {
            "name": _name,
            "privacy": _privacy,
            "channels": _normalize_channels(_channels),
            "context": _ser_list(_context),
            "categories": _ser_list(_categories),
        }
        if _details is not None:
            body["details"] = _details
        if _url is not None:
            body["url"] = _url
        if _main_asset_id is not None:
            body["mainAssetId"] = _main_asset_id
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)

        params = {"hubProfileId": hub_profile_id} if hub_profile_id else None
        data = self._http.put(
            f"/api/v1/contents/{content_id}", json=body, params=params
        )
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            _upload_cover_sync(
                result, _img_bytes, _img_content_type or "application/octet-stream"
            )

        if cover_image is not None:
            return self.get(content_id, hub_profile_id=hub_profile_id)
        return result

    def filter(
        self,
        hub_profile_id: str,
        *,
        page_size: int,
        cursor: str | None = None,
        only_archived: bool = False,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
        types: list[str] | None = None,
    ) -> CursorPagedList[ContentSearch]:
        """
        List content items for a hub profile with cursor-based pagination.

        Returns a page of content summaries for the given hub profile. Supports
        filtering by archive status, content type, and exclusion lists. Pass the
        returned ``cursor`` to subsequent calls to retrieve the next page.

        Use ``paginate()`` from ``sdk.schemas.common`` to iterate all pages
        automatically.

        Args:
            hub_profile_id: ID of the hub profile.
            page_size: Maximum number of items to return per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            only_archived: If True, return only archived content. Defaults to
                False.
            exclude_categories: Category IDs whose content should be excluded.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.
            types: Content types to include — ``"Content"``, ``"Collection"``,
                or both (default).

        Returns:
            CursorPagedList[ContentSearch] with content summaries and an
            optional cursor for the next page.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        page = client.contents.filter(
            "01965f7a-0000-7000-8000-000000000002",
            page_size=20,
            types=["Content"],
        )

        # Or iterate all pages:
        from sdk import paginate

        for item in paginate(
            lambda cursor: client.contents.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=50,
                cursor=cursor,
            )
        ):
            print(item.name)
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                ContentSearch(
                    id="01965f7a-0000-7000-8000-000000000005",
                    name="Welcome to the Team",
                    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                    cover=None,
                    privacy="Public",
                ),
            ],
            cursor=None,
        )
        ```
        """
        body: dict = {
            "pageSize": page_size,
            "onlyArchived": only_archived,
            "excludeCategories": exclude_categories or [],
            "excludeCollections": exclude_collections or [],
            "excludeContents": exclude_contents or [],
            "type": types or ["Content", "Collection"],
        }
        if cursor is not None:
            body["cursor"] = cursor
        data = self._http.post(f"/api/v1/contents/{hub_profile_id}/filter/", json=body)
        items = [ContentSearch.model_validate(i) for i in (data.get("items") or [])]
        return CursorPagedList[ContentSearch](items=items, cursor=data.get("cursor"))

    def search(
        self,
        hub_profile_id: str,
        *,
        search: str,
        only_archived: bool = False,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
    ) -> list[ContentSearch]:
        """
        Search content items in a hub profile by name or keyword.

        Performs a text search across content names in the hub profile.
        Returns a flat list (not paginated) — use ``filter`` for paginated
        browsing.

        Args:
            hub_profile_id: ID of the hub profile to search within.
            search: Search query string (matched against content names).
            only_archived: If True, search only archived content. Defaults
                to False.
            types: Content types to include. All types if omitted.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.

        Returns:
            List of ContentSearch objects matching the query.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        results = client.contents.search(
            "01965f7a-0000-7000-8000-000000000002",
            search="welcome",
        )
        ```

        Example response:
        ```python
        [
            ContentSearch(
                id="01965f7a-0000-7000-8000-000000000005",
                name="Welcome to the Team",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                cover=None,
                privacy="Public",
            ),
        ]
        ```
        """
        body: dict = {"search": search, "onlyArchived": only_archived}
        if types is not None:
            body["type"] = types
        if exclude_categories is not None:
            body["excludeCategories"] = exclude_categories
        if exclude_collections is not None:
            body["excludeCollections"] = exclude_collections
        if exclude_contents is not None:
            body["excludeContents"] = exclude_contents
        data = self._http.post(f"/api/v1/contents/{hub_profile_id}/search", json=body)
        return [ContentSearch.model_validate(item) for item in (data or [])]

    # -- Content category management --

    def add_to_categories(self, content_id: str, body: dict) -> None:
        """
        Add a content item to one or more channel categories.

        Places the content into the specified channel categories. The request
        body schema follows the backend API format (see backend source for
        details).

        Args:
            content_id: ID of the content item.
            body: Request body specifying which channel categories to add
                the content to.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.add_to_categories(
            "01965f7a-0000-7000-8000-000000000005",
            body={
                "contentId": "01965f7a-0000-7000-8000-000000000005",
                "channels": [
                    {
                        "channelId": "01965f7a-0000-7000-8000-000000000003",
                        "categoryIds": ["01965f7a-0000-7000-8000-000000000004"],
                    }
                ],
            },
        )
        ```
        """
        self._http.put("/api/v1/contents/channels/add", json=body)

    def remove_from_categories(self, content_id: str, body: dict) -> None:
        """
        Remove a content item from one or more channel categories.

        Removes the content from the specified channel categories. The
        content item itself is not deleted.

        Args:
            content_id: ID of the content item.
            body: Request body specifying which channel categories to remove
                the content from.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.remove_from_categories(
            "01965f7a-0000-7000-8000-000000000005",
            body={
                "contentId": "01965f7a-0000-7000-8000-000000000005",
                "channels": [
                    {
                        "channelId": "01965f7a-0000-7000-8000-000000000003",
                        "categoryIds": ["01965f7a-0000-7000-8000-000000000004"],
                    }
                ],
            },
        )
        ```
        """
        self._http.put("/api/v1/contents/channels/categories/delete", json=body)

    def move(self, content_id: str, body: dict) -> None:
        """
        Move a content item to a different channel category.

        Relocates the content from its current category position to a new
        one within the same or a different channel.

        Args:
            content_id: ID of the content item.
            body: Request body specifying the source and destination
                category positions.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.move(
            "01965f7a-0000-7000-8000-000000000005",
            body={
                "contentId": "01965f7a-0000-7000-8000-000000000005",
                "fromCategoryId": "01965f7a-0000-7000-8000-000000000004",
                "toCategoryId": "01965f7a-0000-7000-8000-000000000013",
                "channelId": "01965f7a-0000-7000-8000-000000000003",
            },
        )
        ```
        """
        self._http.put(
            f"/api/v1/contents/{content_id}/channels/categories/move-to", json=body
        )

    # -- Content sections --

    def create_section(self, content_id: str, category_name: str, *, name: str) -> None:
        """
        Create a section in a content item's category.

        Adds a named section to the specified category of a collection-type
        content item. Sections group the nested content within a collection.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category to add the section to.
            name: Display name of the new section.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.create_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            name="Day 1",
        )
        ```
        """
        self._http.post(
            f"/api/v1/contents/{content_id}/{category_name}/sections",
            json={"name": name},
        )

    def update_section(
        self, content_id: str, category_name: str, section_id: str, *, name: str
    ) -> None:
        """
        Update the name of a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category containing the section.
            section_id: ID of the section to update.
            name: New display name.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.update_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            "01965f7a-0000-7000-8000-000000000011",
            name="Day 1 (Updated)",
        )
        ```
        """
        self._http.put(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}",
            json={"name": name},
        )

    def delete_section(
        self, content_id: str, category_name: str, section_id: str
    ) -> None:
        """
        Delete a section from a content item's category.

        Permanently removes the section. Content items within the section
        remain in the category but are no longer grouped.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category containing the section.
            section_id: ID of the section to delete.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.delete_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            "01965f7a-0000-7000-8000-000000000011",
        )
        ```
        """
        self._http.delete(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}"
        )

    # -- Progressions --

    def patch_content_progression(
        self, content_id: str, *, status: ProgressionStatus
    ) -> ContentProgression:
        """
        Update the current user's progression status for a content item.

        Records whether the current API key user has started, is in progress
        on, or has completed the specified content item. Progression data is
        used for tracking learner completion within a hub profile.

        Args:
            content_id: ID of the content item.
            status: New progression status — ``"NotStarted"``,
                ``"Incomplete"``, or ``"Completed"``.

        Returns:
            ContentProgression reflecting the updated status.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        progression = client.contents.patch_content_progression(
            "01965f7a-0000-7000-8000-000000000005",
            status="Completed",
        )
        ```

        Example response:
        ```python
        ContentProgression(status="Completed")
        ```
        """
        data = self._http.patch(
            f"/api/v1/progressions/contents/{content_id}",
            json={"status": status},
        )
        if data is None:
            return ContentProgression()
        return ContentProgression.model_validate(data)

    def patch_media_progression(self, media_id: str, *, last_watched_time: int) -> None:
        """
        Update the current user's last watched position in a media asset.

        Records the playback position so the user can resume from where they
        left off. Call this periodically during playback (e.g. every 30
        seconds) and on pause / close.

        Args:
            media_id: ID of the media asset.
            last_watched_time: Playback position in seconds.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        client.contents.patch_media_progression(
            "01965f7a-0000-7000-8000-000000000006",
            last_watched_time=95,
        )
        ```
        """
        self._http.patch(
            f"/api/v1/progressions/medias/{media_id}",
            json={"lastWatchedTime": last_watched_time},
        )

    def get_progression_stats(
        self, *, collection_id: str | None = None
    ) -> CollectionProgressionStats:
        """
        Get progression statistics for the current user.

        Returns the total number of content items and how many the current
        user has completed. Optionally scoped to a single collection.

        Args:
            collection_id: If provided, scopes the stats to the content
                items within that collection.

        Returns:
            CollectionProgressionStats with ``total`` and ``completed``
            counts.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        stats = client.contents.get_progression_stats(
            collection_id="01965f7a-0000-7000-8000-000000000014"
        )
        print(f"{stats.completed}/{stats.total} completed")
        ```

        Example response:
        ```python
        CollectionProgressionStats(total=12, completed=7)
        ```
        """
        params = {"collectionId": collection_id} if collection_id else None
        data = self._http.get("/api/v1/progressions/stats", params=params)
        if data is None:
            return CollectionProgressionStats()
        return CollectionProgressionStats.model_validate(data)

    # -- V2 --

    def get_v2(self, content_id: str) -> ContentV2:
        """
        Get a content item by ID (v2).

        Retrieves the content item using the v2 schema, which additionally
        includes the main playable asset (with its HLS stream URL and
        embed details), the current user's progression, and extended
        metadata.

        Args:
            content_id: ID of the content item to retrieve.

        Returns:
            ContentV2 with extended metadata, main asset, and progression.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        content = client.contents.get_v2("01965f7a-0000-7000-8000-000000000005")
        ```

        Example response:
        ```python
        ContentV2(
            id="01965f7a-0000-7000-8000-000000000005",
            privacy="Public",
            name="Welcome to the Team",
            details="Everything you need to know for your first week.",
            url=None,
            created_by="01965f7a-0000-7000-8000-000000000007",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            main_asset=MainPlayableAsset(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Intro Video",
                cover=None,
                duration_in_seconds=120,
                url=None,
                iframe_url=None,
                external_media_id=None,
                hls_stream_url="https://stream.srgplus.com/hls/intro-video/playlist.m3u8",
                original_stream_url=None,
                status="ready",
                progression=MediaProgression(
                    last_watched_time=95,
                    status="Incomplete",
                ),
            ),
            context=[],
            created="2025-06-01T10:00:00Z",
            archived=None,
            cover=None,
            channels=[],
            categories=[],
            progression=ContentProgression(status="Incomplete"),
        )
        ```
        """
        data = self._http.get(f"/api/v2/contents/{content_id}")
        return ContentV2.model_validate(data)

    def filter_all(
        self,
        hub_profile_id: str,
        *,
        page_size: int = 50,
        only_archived: bool = False,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
        types: list[str] | None = None,
    ) -> Iterator[ContentSearch]:
        """
        Iterate over all content items for a hub profile across all pages.

        Wraps :meth:`filter` and handles cursor-based pagination automatically.
        Yields individual :class:`~srg.schemas.content.ContentSearch` items.

        Args:
            hub_profile_id: ID of the hub profile.
            page_size: Items per page. Defaults to 50.
            only_archived: If True, return only archived content.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.
            types: Content types to include (``"Content"``, ``"Collection"``).

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        for content in client.contents.filter_all(hub_profile_id):
            print(content.name)
        ```
        """
        cursor: str | None = None
        while True:
            page = self.filter(
                hub_profile_id,
                page_size=page_size,
                cursor=cursor,
                only_archived=only_archived,
                exclude_categories=exclude_categories,
                exclude_collections=exclude_collections,
                exclude_contents=exclude_contents,
                types=types,
            )
            yield from page.items
            cursor = page.cursor
            if cursor is None:
                break

    def search_all(
        self,
        hub_profile_id: str,
        *,
        search: str,
        only_archived: bool = False,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
    ) -> Iterator[ContentSearch]:
        """
        Iterate over all content search results as an iterator.

        Wraps :meth:`search` and returns results as a lazy iterator for a
        consistent interface with :meth:`filter_all`.

        Args:
            hub_profile_id: ID of the hub profile.
            search: Search query string.
            only_archived: If True, search only archived content.
            types: Content types to include.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        for content in client.contents.search_all(hub_profile_id, search="intro"):
            print(content.name)
        ```
        """
        yield from self.search(
            hub_profile_id,
            search=search,
            only_archived=only_archived,
            types=types,
            exclude_categories=exclude_categories,
            exclude_collections=exclude_collections,
            exclude_contents=exclude_contents,
        )


class AsyncContentsResource:
    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str,
        hub_profile_id: str,
        privacy: ContentPrivacy = "Preview",
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: Any | None = None,  # noqa: ANN401
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
    ) -> Content | ContentUploadSignedUrl:
        """
        Create a new content item in a hub profile.

        Creates a content item or collection inside the given hub profile.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image and returns the fully
        populated :class:`~srg.schemas.content.Content`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
        signed URL so you can upload the image yourself.

        Args:
            name: Display title of the content item.
            hub_profile_id: ID of the hub profile to create the content in.
            privacy: Visibility — ``"Preview"`` (default), ``"Private"``,
                or ``"Public"``.
            details: Optional body text / description.
            url: Optional external URL.
            main_asset_id: ID of the primary playable asset.
            cover_image: Local path or ``http(s)://`` URL of the cover image.
                Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            channels: Channel and category placements.
            context: Additional context objects.
            categories: Category assignments.

        Returns:
            :class:`~srg.schemas.content.Content` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            content = await client.contents.create(
                name="Welcome to the Team",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                privacy="Public",
                main_asset_id="01965f7a-0000-7000-8000-000000000006",
                cover_image="/path/to/cover.jpg",
            )
        ```

        Example response:
        ```python
        Content(
            id="01965f7a-0000-7000-8000-000000000005",
            name="Welcome to the Team",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            cover=ContentCover(
                urls=CoverUrls(
                    original="https://cdn.srgplus.com/covers/welcome.jpg",
                ),
                extension="jpg",
                modified="2025-06-01T10:00:00Z",
            ),
            channels=[],
        )
        ```
        """
        _img_bytes: bytes | None = None
        _img_content_type: str | None = None

        if cover_image is not None and cover is None:
            _img_bytes, _img_content_type = await read_image_async(cover_image)
            cover = _make_image_upsert(_img_bytes, cover_image)

        body: dict = {
            "name": name,
            "hubProfileId": hub_profile_id,
            "privacy": privacy,
            "channels": _normalize_channels(channels),
            "context": _ser_list(context or []),
            "categories": _ser_list(categories or []),
        }
        if details is not None:
            body["details"] = details
        if url is not None:
            body["url"] = url
        if main_asset_id is not None:
            body["mainAssetId"] = main_asset_id
        if cover is not None:
            body["cover"] = (
                cover.model_dump(by_alias=True, exclude_none=True)
                if isinstance(cover, BaseModel)
                else cover
            )
        data = await self._http.post("/api/v1/contents", json=body)
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            await _upload_cover_async(
                result, _img_bytes, _img_content_type or "application/octet-stream"
            )

        if cover_image is not None:
            return await self.get(result.id, hub_profile_id=hub_profile_id)
        return result

    async def get(
        self, content_id: str, *, hub_profile_id: str | None = None
    ) -> Content:
        """
        Get a content item by ID (v1).

        Args:
            content_id: ID of the content item to retrieve.
            hub_profile_id: If provided, used to resolve access context.

        Returns:
            Content object with metadata and channel placement details.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            content = await client.contents.get(
                "01965f7a-0000-7000-8000-000000000005"
            )
        ```

        Example response:
        ```python
        Content(
            id="01965f7a-0000-7000-8000-000000000005",
            name="Welcome to the Team",
            details="Everything you need to know for your first week.",
            url=None,
            created_by="01965f7a-0000-7000-8000-000000000007",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            created="2025-06-01T10:00:00Z",
            archived=None,
            cover=None,
            channels=[],
            heading_referenced_content=[],
        )
        ```
        """
        params = {"hubProfileId": hub_profile_id} if hub_profile_id else None
        data = await self._http.get(f"/api/v1/contents/{content_id}", params=params)
        return Content.model_validate(data)

    async def update(
        self,
        content_id: str,
        *,
        name: str | None = None,
        hub_profile_id: str | None = None,
        privacy: ContentPrivacy | None = None,
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: ContentFileUploadParameters | None = None,
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
    ) -> Content | ContentUploadSignedUrl:
        """
        Update a content item's metadata.

        Fetches the current state first, then merges the provided values.
        Fields left as ``None`` are preserved from the existing content —
        only explicitly passed values are changed.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or
        an ``http(s)://`` URL. The SDK uploads the image and returns the
        updated :class:`~srg.schemas.content.Content`. **Manual mode** — pass
        ``cover`` to get back
        :class:`~srg.schemas.content.ContentUploadSignedUrl`.

        Args:
            content_id: ID of the content item.
            name: New display title. Keeps existing if ``None``.
            hub_profile_id: Hub profile that owns this content.
            privacy: New visibility level. Keeps existing if ``None``.
            details: New body text. Keeps existing if ``None``.
            url: New external URL. Keeps existing if ``None``.
            main_asset_id: New primary asset ID. Keeps existing if ``None``.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover upload parameters (manual mode).
            channels: Channel/category placements. Keeps existing if ``None``.
            context: Context widgets. Keeps existing if ``None``.
            categories: Category assignments. Keeps existing if ``None``.

        Returns:
            :class:`~srg.schemas.content.Content` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            # Only name changes; channels/context/categories are preserved.
            content = await client.contents.update(
                "01965f7a-0000-7000-8000-000000000005",
                name="Welcome to the Team (v2)",
                privacy="Public",
            )
        ```
        """
        existing = await self.get_v2(content_id)

        _name = name if name is not None else existing.name
        _privacy = privacy if privacy is not None else existing.privacy
        _details = details if details is not None else existing.details
        _url = url if url is not None else existing.url
        _main_asset_id = (
            main_asset_id
            if main_asset_id is not None
            else (existing.main_asset.id if existing.main_asset else None)
        )
        _channels: list[str | ContentChannelUpsert] = (
            channels
            if channels is not None
            else [
                ContentChannelUpsert(
                    channel_id=ch.id,
                    category_ids=[c.id for c in ch.categories],
                )
                for ch in existing.channels
            ]
        )
        _context = context if context is not None else existing.context
        _categories = categories if categories is not None else existing.categories

        _img_bytes: bytes | None = None
        _img_content_type: str | None = None

        if cover_image is not None and cover is None:
            _img_bytes, _img_content_type = await read_image_async(cover_image)
            cover = _make_content_file_params(_img_bytes, cover_image)

        body: dict = {
            "name": _name,
            "privacy": _privacy,
            "channels": _normalize_channels(_channels),
            "context": _ser_list(_context),
            "categories": _ser_list(_categories),
        }

        if _details is not None:
            body["details"] = _details
        if _url is not None:
            body["url"] = _url
        if _main_asset_id is not None:
            body["mainAssetId"] = _main_asset_id
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)

        params = {"hubProfileId": hub_profile_id} if hub_profile_id else None
        data = await self._http.put(
            f"/api/v1/contents/{content_id}", json=body, params=params
        )
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            await _upload_cover_async(
                result, _img_bytes, _img_content_type or "application/octet-stream"
            )

        if cover_image is not None:
            return await self.get(content_id, hub_profile_id=hub_profile_id)
        return result

    async def filter(
        self,
        hub_profile_id: str,
        *,
        page_size: int,
        cursor: str | None = None,
        only_archived: bool = False,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
        types: list[str] | None = None,
    ) -> CursorPagedList[ContentSearch]:
        """
        List content items for a hub profile with cursor-based pagination.

        Args:
            hub_profile_id: ID of the hub profile.
            page_size: Maximum number of items per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            only_archived: If True, return only archived content.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.
            types: Content types to include (defaults to both ``"Content"``
                and ``"Collection"``).

        Returns:
            CursorPagedList[ContentSearch] with content summaries and an
            optional cursor for the next page.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            page = await client.contents.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=20,
            )
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                ContentSearch(
                    id="01965f7a-0000-7000-8000-000000000005",
                    name="Welcome to the Team",
                    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                    cover=None,
                    privacy="Public",
                ),
            ],
            cursor=None,
        )
        ```
        """
        body: dict = {
            "pageSize": page_size,
            "onlyArchived": only_archived,
            "excludeCategories": exclude_categories or [],
            "excludeCollections": exclude_collections or [],
            "excludeContents": exclude_contents or [],
            "type": types or ["Content", "Collection"],
        }
        if cursor is not None:
            body["cursor"] = cursor
        data = await self._http.post(
            f"/api/v1/contents/{hub_profile_id}/filter/", json=body
        )
        items = [ContentSearch.model_validate(i) for i in (data.get("items") or [])]

        return CursorPagedList[ContentSearch](items=items, cursor=data.get("cursor"))

    async def search(
        self,
        hub_profile_id: str,
        *,
        search: str,
        only_archived: bool = False,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
    ) -> list[ContentSearch]:
        """
        Search content items in a hub profile by name or keyword.

        Args:
            hub_profile_id: ID of the hub profile.
            search: Search query string.
            only_archived: If True, search only archived content.
            types: Content types to include.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_contents: Content IDs to exclude.

        Returns:
            List of ContentSearch objects matching the query.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            results = await client.contents.search(
                "01965f7a-0000-7000-8000-000000000002",
                search="welcome",
            )
        ```

        Example response:
        ```python
        [
            ContentSearch(
                id="01965f7a-0000-7000-8000-000000000005",
                name="Welcome to the Team",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                cover=None,
                privacy="Public",
            ),
        ]
        ```
        """
        body: dict = {"search": search, "onlyArchived": only_archived}
        if types is not None:
            body["type"] = types
        if exclude_categories is not None:
            body["excludeCategories"] = exclude_categories
        if exclude_collections is not None:
            body["excludeCollections"] = exclude_collections
        if exclude_contents is not None:
            body["excludeContents"] = exclude_contents
        data = await self._http.post(
            f"/api/v1/contents/{hub_profile_id}/search", json=body
        )
        return [ContentSearch.model_validate(item) for item in (data or [])]

    async def add_to_categories(self, content_id: str, body: dict) -> None:
        """
        Add a content item to one or more channel categories.

        Args:
            content_id: ID of the content item.
            body: Request body specifying which channel categories to add
                the content to.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.add_to_categories(
                "01965f7a-0000-7000-8000-000000000005",
                body={
                    "contentId": "01965f7a-0000-7000-8000-000000000005",
                    "channels": [
                        {
                            "channelId": "01965f7a-0000-7000-8000-000000000003",
                            "categoryIds": ["01965f7a-0000-7000-8000-000000000004"],
                        }
                    ],
                },
            )
        ```
        """
        await self._http.put("/api/v1/contents/channels/add", json=body)

    async def remove_from_categories(self, content_id: str, body: dict) -> None:
        """
        Remove a content item from one or more channel categories.

        Args:
            content_id: ID of the content item.
            body: Request body specifying which channel categories to remove
                the content from.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.remove_from_categories(
                "01965f7a-0000-7000-8000-000000000005",
                body={
                    "contentId": "01965f7a-0000-7000-8000-000000000005",
                    "channels": [
                        {
                            "channelId": "01965f7a-0000-7000-8000-000000000003",
                            "categoryIds": ["01965f7a-0000-7000-8000-000000000004"],
                        }
                    ],
                },
            )
        ```
        """
        await self._http.put("/api/v1/contents/channels/categories/delete", json=body)

    async def move(self, content_id: str, body: dict) -> None:
        """
        Move a content item to a different channel category.

        Args:
            content_id: ID of the content item.
            body: Request body with source and destination category positions.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.move(
                "01965f7a-0000-7000-8000-000000000005",
                body={
                    "contentId": "01965f7a-0000-7000-8000-000000000005",
                    "fromCategoryId": "01965f7a-0000-7000-8000-000000000004",
                    "toCategoryId": "01965f7a-0000-7000-8000-000000000013",
                    "channelId": "01965f7a-0000-7000-8000-000000000003",
                },
            )
        ```
        """
        await self._http.put(
            f"/api/v1/contents/{content_id}/channels/categories/move-to", json=body
        )

    async def create_section(
        self, content_id: str, category_name: str, *, name: str
    ) -> None:
        """
        Create a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            name: Display name of the new section.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.create_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                name="Day 1",
            )
        ```
        """
        await self._http.post(
            f"/api/v1/contents/{content_id}/{category_name}/sections",
            json={"name": name},
        )

    async def update_section(
        self, content_id: str, category_name: str, section_id: str, *, name: str
    ) -> None:
        """
        Update the name of a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            section_id: ID of the section to update.
            name: New display name.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.update_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                "01965f7a-0000-7000-8000-000000000011",
                name="Day 1 (Updated)",
            )
        ```
        """
        await self._http.put(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}",
            json={"name": name},
        )

    async def delete_section(
        self, content_id: str, category_name: str, section_id: str
    ) -> None:
        """
        Delete a section from a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            section_id: ID of the section to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.delete_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                "01965f7a-0000-7000-8000-000000000011",
            )
        ```
        """
        await self._http.delete(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}"
        )

    async def patch_content_progression(
        self, content_id: str, *, status: ProgressionStatus
    ) -> ContentProgression:
        """
        Update the current user's progression status for a content item.

        Args:
            content_id: ID of the content item.
            status: New status — ``"NotStarted"``, ``"Incomplete"``, or
                ``"Completed"``.

        Returns:
            ContentProgression reflecting the updated status.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            progression = await client.contents.patch_content_progression(
                "01965f7a-0000-7000-8000-000000000005",
                status="Completed",
            )
        ```

        Example response:
        ```python
        ContentProgression(status="Completed")
        ```
        """
        data = await self._http.patch(
            f"/api/v1/progressions/contents/{content_id}",
            json={"status": status},
        )
        if data is None:
            return ContentProgression()
        return ContentProgression.model_validate(data)

    async def patch_media_progression(
        self, media_id: str, *, last_watched_time: int
    ) -> None:
        """
        Update the current user's last watched position in a media asset.

        Args:
            media_id: ID of the media asset.
            last_watched_time: Playback position in seconds.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            await client.contents.patch_media_progression(
                "01965f7a-0000-7000-8000-000000000006",
                last_watched_time=95,
            )
        ```
        """
        await self._http.patch(
            f"/api/v1/progressions/medias/{media_id}",
            json={"lastWatchedTime": last_watched_time},
        )

    async def get_progression_stats(
        self, *, collection_id: str | None = None
    ) -> CollectionProgressionStats:
        """
        Get progression statistics for the current user.

        Args:
            collection_id: If provided, scopes the stats to the content
                items within that collection.

        Returns:
            CollectionProgressionStats with ``total`` and ``completed``
            counts.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            stats = await client.contents.get_progression_stats(
                collection_id="01965f7a-0000-7000-8000-000000000014"
            )
        ```

        Example response:
        ```python
        CollectionProgressionStats(total=12, completed=7)
        ```
        """
        params = {"collectionId": collection_id} if collection_id else None
        data = await self._http.get("/api/v1/progressions/stats", params=params)
        if data is None:
            return CollectionProgressionStats()
        return CollectionProgressionStats.model_validate(data)

    # -- V2 --

    async def get_v2(self, content_id: str) -> ContentV2:
        """
        Get a content item by ID (v2).

        Retrieves the content item using the v2 schema, which additionally
        includes the main playable asset, the current user's progression,
        and extended metadata.

        Args:
            content_id: ID of the content item to retrieve.

        Returns:
            ContentV2 with extended metadata, main asset, and progression.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            content = await client.contents.get_v2(
                "01965f7a-0000-7000-8000-000000000005"
            )
        ```

        Example response:
        ```python
        ContentV2(
            id="01965f7a-0000-7000-8000-000000000005",
            privacy="Public",
            name="Welcome to the Team",
            details="Everything you need to know for your first week.",
            url=None,
            created_by="01965f7a-0000-7000-8000-000000000007",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            hub_profile_name="Acme Academy",
            main_asset=MainPlayableAsset(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Intro Video",
                cover=None,
                duration_in_seconds=120,
                hls_stream_url="https://stream.srgplus.com/hls/intro-video/playlist.m3u8",
                status="ready",
                progression=MediaProgression(
                    last_watched_time=95,
                    status="Incomplete",
                ),
            ),
            context=[],
            created="2025-06-01T10:00:00Z",
            archived=None,
            cover=None,
            channels=[],
            categories=[],
            progression=ContentProgression(status="Incomplete"),
        )
        ```
        """
        data = await self._http.get(f"/api/v2/contents/{content_id}")
        return ContentV2.model_validate(data)

    async def filter_all(
        self,
        hub_profile_id: str,
        *,
        page_size: int = 50,
        only_archived: bool = False,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
        types: list[str] | None = None,
    ) -> AsyncIterator[ContentSearch]:
        """
        Async-iterate over all content items for a hub profile across all pages.

        Wraps :meth:`filter` and handles cursor-based pagination automatically.
        Yields individual :class:`~srg.schemas.content.ContentSearch` items.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            async for content in client.contents.filter_all(hub_profile_id):
                print(content.name)
        ```
        """
        cursor: str | None = None
        while True:
            page = await self.filter(
                hub_profile_id,
                page_size=page_size,
                cursor=cursor,
                only_archived=only_archived,
                exclude_categories=exclude_categories,
                exclude_collections=exclude_collections,
                exclude_contents=exclude_contents,
                types=types,
            )
            for item in page.items:
                yield item
            cursor = page.cursor
            if cursor is None:
                break

    async def search_all(
        self,
        hub_profile_id: str,
        *,
        search: str,
        only_archived: bool = False,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_contents: list[str] | None = None,
    ) -> AsyncIterator[ContentSearch]:
        """
        Async-iterate over all content search results.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            async for content in client.contents.search_all(
                hub_profile_id, search="intro"
            ):
                print(content.name)
        ```
        """
        for item in await self.search(
            hub_profile_id,
            search=search,
            only_archived=only_archived,
            types=types,
            exclude_categories=exclude_categories,
            exclude_collections=exclude_collections,
            exclude_contents=exclude_contents,
        ):
            yield item
