from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg._upload import (
    image_content_type,
    put_bytes_to_signed_url,
    put_bytes_to_signed_url_async,
    read_image_async,
    read_image_sync,
    resolve_image_extension,
)
from srg._upload_multipart import get_image_dimensions_from_bytes
from srg.exceptions import SRGError
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
    CreatedSection,
    SubcontentItem,
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


def _make_image_upsert(
    img_bytes: bytes, source: str | Path, content_type: str | None = None
) -> ImageUpsert:
    """Describe a cover image from its bytes: real type and real dimensions.

    The type comes from the magic bytes first, so a URL without an extension
    (e.g. a signed Drive asset URL) still works.
    """
    ext = resolve_image_extension(img_bytes, source, content_type)
    if not ext:
        where = str(source).split("?")[0]
        raise SRGError(
            f"Could not tell the image type of {where}: the bytes are not a "
            "recognised image and there is no extension or image Content-Type."
        )
    dims = get_image_dimensions_from_bytes(img_bytes)
    width, height = (int(dims[0]), int(dims[1])) if dims else (1, 1)
    return ImageUpsert(width=width, height=height, size=len(img_bytes), extension=ext)


def _make_content_file_params(
    img_bytes: bytes, source: str | Path, content_type: str | None = None
) -> ContentFileUploadParameters:
    return ContentFileUploadParameters(
        image=_make_image_upsert(img_bytes, source, content_type),
        generate_signed_url=True,
    )


def _ser_cover(cover: Any) -> dict:  # noqa: ANN401
    """Serialize a cover upsert for the API.

    ``image`` is a required property on the backend DTO, so it must be present
    even when null (``{"image": null, "generateSignedUrl": false}`` = keep).
    """
    data = (
        cover.model_dump(by_alias=True, exclude_none=True)
        if isinstance(cover, BaseModel)
        else dict(cover)
    )
    data.setdefault("image", None)
    return data


def _build_patch_body(
    *,
    name: str | None,
    privacy: str | None,
    details: str | None,
    url: str | None,
    main_asset_id: str | None,
    cover: Any | None,  # noqa: ANN401
    channels: list[Any] | None,
    context: list[Any] | None,
    categories: list[Any] | None,
) -> dict:
    """Body for PATCH /contents/{id}: only the fields the caller supplied.

    The backend keeps the stored value of every omitted field — cover, main
    asset, channels, categories, action buttons — so a body-only edit can
    never wipe them.
    """
    body: dict = {}
    if name is not None:
        body["name"] = name
    if privacy is not None:
        body["privacy"] = privacy
    if details is not None:
        body["details"] = details
    if url is not None:
        body["url"] = url
    if main_asset_id is not None:
        body["mainAssetId"] = main_asset_id
    if channels is not None:
        body["channels"] = _normalize_channels(channels)
    if context is not None:
        body["context"] = _ser_list(context)
    if categories is not None:
        body["categories"] = _ser_list(categories)
    if cover is not None:
        body["cover"] = _ser_cover(cover)
    return body


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
        privacy: ContentPrivacy = "Preview",
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: Any | None = None,
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
        workspace_id: str,
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

        client = SRGClient(api_keys=["srgplus_your_key"])
        content = client.contents.create(
            name="Welcome to the Team",
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            privacy="Public",
            details="Everything you need to know for your first week.",
            main_asset_id="01965f7a-0000-7000-8000-000000000006",
            cover_image="/path/to/cover.jpg",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        _upload_type = "application/octet-stream"

        if cover_image is not None and cover is None:
            _img_bytes, _served_type = read_image_sync(cover_image)
            cover = _make_image_upsert(_img_bytes, cover_image, _served_type)
            # The signed URL is bound to the MIME of the declared extension.
            _upload_type = image_content_type(cover.extension, _served_type)

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
        data = self._get_http(workspace_id).post("/api/v1/contents", json=body)
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            _upload_cover_sync(result, _img_bytes, _upload_type)

        if cover_image is not None:
            return self.get(
                result.id, hub_profile_id=hub_profile_id, workspace_id=workspace_id
            )
        return result

    def get(
        self, content_id: str, *, hub_profile_id: str | None = None, workspace_id: str
    ) -> Content:
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        content = client.contents.get(
            "01965f7a-0000-7000-8000-000000000005",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = self._get_http(workspace_id).get(
            f"/api/v1/contents/{content_id}", params=params
        )
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
        workspace_id: str,
    ) -> Content | ContentUploadSignedUrl:
        """
        Update a content item. Only the fields you pass are changed.

        Sends ``PATCH /api/v1/contents/{id}`` with just the supplied fields.
        The backend keeps the stored value of every omitted field, so an
        update that doesn't mention the cover, main asset, channels,
        categories or action buttons never wipes them (the old
        GET-merge-PUT approach did: PUT treats an omitted cover as "remove").

        Lists you DO pass — ``channels``, ``context``, ``categories`` —
        replace the stored list. To append, read the content first
        (:meth:`get_v2`) and send the full new list.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or
        an ``http(s)://`` URL (an extension is not required: the image type
        is read from the bytes). The SDK uploads the image and returns the
        updated :class:`~srg.schemas.content.Content`.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
        signed URL so you can upload the image yourself.

        To use an image that is already in the hub Drive as the cover, call
        :meth:`set_cover_from_asset` instead.

        Args:
            content_id: ID of the content item to update.
            name: New display title. Unchanged if ``None``.
            hub_profile_id: Hub profile that owns this content. Resolved from
                the content when omitted (one extra GET).
            privacy: New visibility level. Unchanged if ``None``.
            details: New body text. Unchanged if ``None``.
            url: New external URL. Unchanged if ``None``.
            main_asset_id: New primary asset ID. Unchanged if ``None``.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            channels: Channel/category placements. Unchanged if ``None``.
            context: Context widgets (the body). Unchanged if ``None``.
            categories: Category options. Unchanged if ``None``.

        Returns:
            :class:`~srg.schemas.content.Content` when ``cover_image`` is
            provided (auto-upload mode).
            :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        # Only the body changes; cover, channels and categories stay as they are.
        client.contents.update(
            "01965f7a-0000-7000-8000-000000000005",
            context=[{"$type": "Text", "content": "New caption"}],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        if hub_profile_id is None:
            hub_profile_id = self.get_v2(
                content_id, workspace_id=workspace_id
            ).hub_profile_id

        _img_bytes: bytes | None = None
        _upload_type = "application/octet-stream"

        if cover_image is not None and cover is None:
            _img_bytes, _served_type = read_image_sync(cover_image)
            cover = _make_content_file_params(_img_bytes, cover_image, _served_type)
            if cover.image is not None:
                _upload_type = image_content_type(cover.image.extension, _served_type)

        body = _build_patch_body(
            name=name,
            privacy=privacy,
            details=details,
            url=url,
            main_asset_id=main_asset_id,
            cover=cover,
            channels=channels,
            context=context,
            categories=categories,
        )

        data = self._get_http(workspace_id).patch(
            f"/api/v1/contents/{content_id}",
            json=body,
            params={"hubProfileId": hub_profile_id},
        )
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            _upload_cover_sync(result, _img_bytes, _upload_type)

        if cover_image is not None:
            return self.get(
                content_id, hub_profile_id=hub_profile_id, workspace_id=workspace_id
            )
        return result

    def set_cover_from_asset(
        self,
        content_id: str,
        asset_id: str,
        *,
        hub_profile_id: str | None = None,
        workspace_id: str,
    ) -> None:
        """
        Use an image that is already in the hub Drive as the content's cover.

        Calls ``POST /api/v1/contents/{id}/cover/from-asset``. The backend
        copies the asset's original bytes into the content cover (so the cover
        survives deletion of the source asset) and regenerates the thumbnails.
        The asset must be an Image whose upload has finished; right after an
        upload the backend may still answer 400 "still uploading" for a few
        seconds — retry.

        Args:
            content_id: ID of the content item.
            asset_id: ID of an Image asset in the same hub.
            hub_profile_id: Owning hub profile. Resolved from the content
                when omitted (one extra GET).
        """
        if hub_profile_id is None:
            hub_profile_id = self.get_v2(
                content_id, workspace_id=workspace_id
            ).hub_profile_id
        self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/cover/from-asset",
            json={"coverAssetId": asset_id},
            params={"hubProfileId": hub_profile_id},
        )

    def archive(self, content_id: str, *, workspace_id: str) -> None:
        """Archive a content item. Reversible — see :meth:`restore`.

        Archiving hides the content from listings; the platform has no hard
        delete for content. Requires ManageArchivation on the owning hub.
        """
        self._get_http(workspace_id).post(f"/api/v1/contents/{content_id}/archive")

    def restore(self, content_id: str, *, workspace_id: str) -> None:
        """Restore a previously archived content item."""
        self._get_http(workspace_id).post(f"/api/v1/contents/{content_id}/restore")

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
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        page = client.contents.filter(
            "01965f7a-0000-7000-8000-000000000002",
            page_size=20,
            types=["Content"],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )

        # Or iterate all pages:
        from sdk import paginate

        for item in paginate(
            lambda cursor: client.contents.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=50,
                cursor=cursor,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = self._get_http(workspace_id).post(
            f"/api/v1/contents/{hub_profile_id}/filter/", json=body
        )
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
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        results = client.contents.search(
            "01965f7a-0000-7000-8000-000000000002",
            search="welcome",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = self._get_http(workspace_id).post(
            f"/api/v1/contents/{hub_profile_id}/search", json=body
        )
        return [ContentSearch.model_validate(item) for item in (data or [])]

    # -- Content category management --

    def add_to_categories(
        self,
        content_id: str,
        *,
        channels_categories: list[ContentChannelUpsert],
        workspace_id: str,
    ) -> None:
        """
        Add a content item to one or more channel categories.

        Args:
            content_id: ID of the content item.
            channels_categories: Channel and category placements to add the
                content to.

        Example:
        ```python
        from srg.schemas.content import ContentChannelUpsert

        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.add_to_categories(
            "01965f7a-0000-7000-8000-000000000005",
            channels_categories=[
                ContentChannelUpsert(
                    channel_id="01965f7a-0000-7000-8000-000000000003",
                    category_ids=["01965f7a-0000-7000-8000-000000000004"],
                )
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body = {
            "contentId": content_id,
            "channelsCategories": _ser_list(channels_categories),
        }
        self._get_http(workspace_id).put("/api/v1/contents/channels/add", json=body)

    def remove_from_categories(
        self,
        content_id: str,
        *,
        channels_categories: list[ContentChannelUpsert],
        workspace_id: str,
    ) -> None:
        """
        Remove a content item from one or more channel categories.

        The content item itself is not deleted.

        Args:
            content_id: ID of the content item.
            channels_categories: Channel and category placements to remove
                the content from.

        Example:
        ```python
        from srg.schemas.content import ContentChannelUpsert

        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.remove_from_categories(
            "01965f7a-0000-7000-8000-000000000005",
            channels_categories=[
                ContentChannelUpsert(
                    channel_id="01965f7a-0000-7000-8000-000000000003",
                    category_ids=["01965f7a-0000-7000-8000-000000000004"],
                )
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body = {
            "contentId": content_id,
            "channelsCategories": _ser_list(channels_categories),
        }
        self._get_http(workspace_id).put(
            "/api/v1/contents/channels/categories/delete", json=body
        )

    def move(
        self,
        content_id: str,
        *,
        channel_id: str,
        category_id: str,
        section_id: str,
        workspace_id: str,
    ) -> None:
        """
        Move a content item to a different channel category.

        Args:
            content_id: ID of the content item.
            channel_id: ID of the channel containing the target category.
            category_id: ID of the destination category.
            section_id: ID of the destination section within the category.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.move(
            "01965f7a-0000-7000-8000-000000000005",
            channel_id="01965f7a-0000-7000-8000-000000000003",
            category_id="01965f7a-0000-7000-8000-000000000013",
            section_id="01965f7a-0000-7000-8000-000000000011",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        body = {
            "channelId": channel_id,
            "categoryId": category_id,
            "sectionId": section_id,
        }
        self._get_http(workspace_id).put(
            f"/api/v1/contents/{content_id}/channels/categories/move-to", json=body
        )

    # -- Content sections --

    def create_section(
        self,
        content_id: str,
        category_name: str,
        *,
        name: str,
        workspace_id: str,
    ) -> CreatedSection:
        """
        Create a section in a content item's category.

        Adds a named section to the specified category of a collection-type
        content item. Sections group the nested content within a collection.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category to add the section to.
            name: Display name of the new section.

        Returns:
            CreatedSection with the ID of the newly created section.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        result = client.contents.create_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            name="Day 1",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        print(result.id)
        ```
        """
        data = self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}/sections",
            json={"name": name},
        )
        return CreatedSection.model_validate(data)

    def update_section(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        name: str,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the name of a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category containing the section.
            section_id: ID of the section to update.
            name: New display name.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.update_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            "01965f7a-0000-7000-8000-000000000011",
            name="Day 1 (Updated)",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).put(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}",
            json={"name": name},
        )

    def delete_section(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.delete_section(
            "01965f7a-0000-7000-8000-000000000005",
            "week-1",
            "01965f7a-0000-7000-8000-000000000011",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}"
        )

    # -- Subcontent (collection child items) --

    def add_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        subcontent_ids: list[str],
        workspace_id: str,
    ) -> None:
        """
        Add content items as subcontent inside a collection section.

        After calling this the content becomes a Collection
        (``IsCollection()`` returns true on the server side).

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section to add subcontent into.
            subcontent_ids: IDs of the content items to nest inside the collection.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.add_subcontent(
            "01965f7a-0000-7000-8000-000000000005",
            "Content",
            "01965f7a-0000-7000-8000-000000000011",
            subcontent_ids=[
                "01965f7a-0000-7000-8000-000000000020",
                "01965f7a-0000-7000-8000-000000000021",
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}/{section_id}/references",
            json={"referenceIds": subcontent_ids},
        )

    def get_subcontent(
        self,
        content_id: str,
        category_name: str,
        *,
        page_size: int,
        cursor: str | None = None,
        order: str = "Asc",
        workspace_id: str,
    ) -> CursorPagedList[SubcontentItem]:
        """
        Get paginated subcontent (child items) of a collection.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            page_size: Maximum number of items to return per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            order: Sort order — ``"Asc"`` (default) or ``"Desc"``.

        Returns:
            CursorPagedList[SubcontentItem] with items and an optional cursor
            for the next page.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        page = client.contents.get_subcontent(
            "01965f7a-0000-7000-8000-000000000005",
            "Content",
            page_size=20,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        for item in page.items:
            print(item.id, item.name)
        ```
        """
        params: dict = {"pageSize": page_size, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        data = self._get_http(workspace_id).get(
            f"/api/v1/contents/{content_id}/{category_name}/references",
            params=params,
        )
        items = [SubcontentItem.model_validate(i) for i in (data.get("items") or [])]
        return CursorPagedList[SubcontentItem](items=items, cursor=data.get("cursor"))

    def delete_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        subcontent_id: str,
        workspace_id: str,
    ) -> None:
        """
        Remove a subcontent item from a collection section.

        The subcontent item itself is not deleted — only the link is removed.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section containing the subcontent.
            subcontent_id: ID of the subcontent item to remove.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.delete_subcontent(
            "01965f7a-0000-7000-8000-000000000005",
            "Content",
            "01965f7a-0000-7000-8000-000000000011",
            "01965f7a-0000-7000-8000-000000000020",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).delete(
            f"/api/v1/contents/{content_id}/{category_name}"
            f"/{section_id}/references/{subcontent_id}",
        )

    def move_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        subcontent_id: str,
        previous_subcontent_id: str | None = None,
        workspace_id: str,
    ) -> None:
        """
        Reorder a subcontent item within a collection section.

        Moves ``subcontent_id`` to the position immediately after
        ``previous_subcontent_id``. Pass ``None`` to move it to the first
        position.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section containing the subcontent.
            subcontent_id: ID of the subcontent item to move.
            previous_subcontent_id: ID of the item that should precede the
                moved item. ``None`` moves it to the first position.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.move_subcontent(
            "01965f7a-0000-7000-8000-000000000005",
            "Content",
            "01965f7a-0000-7000-8000-000000000011",
            subcontent_id="01965f7a-0000-7000-8000-000000000021",
            previous_subcontent_id="01965f7a-0000-7000-8000-000000000020",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}"
            f"/{section_id}/references/move",
            json={
                "referenceId": subcontent_id,
                "previousReferenceId": previous_subcontent_id,
            },
        )

    # -- Progressions --

    def patch_content_progression(
        self,
        content_id: str,
        *,
        status: ProgressionStatus,
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        progression = client.contents.patch_content_progression(
            "01965f7a-0000-7000-8000-000000000005",
            status="Completed",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        ContentProgression(status="Completed")
        ```
        """
        data = self._get_http(workspace_id).patch(
            f"/api/v1/progressions/contents/{content_id}",
            json={"status": status},
        )
        if data is None:
            return ContentProgression()
        return ContentProgression.model_validate(data)

    def patch_media_progression(
        self,
        media_id: str,
        *,
        last_watched_time: int,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the current user's last watched position in a media asset.

        Records the playback position so the user can resume from where they
        left off. Call this periodically during playback (e.g. every 30
        seconds) and on pause / close.

        Args:
            media_id: ID of the media asset.
            last_watched_time: Playback position in seconds.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        client.contents.patch_media_progression(
            "01965f7a-0000-7000-8000-000000000006",
            last_watched_time=95,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```
        """
        return self._get_http(workspace_id).patch(
            f"/api/v1/progressions/medias/{media_id}",
            json={"lastWatchedTime": last_watched_time},
        )

    def get_progression_stats(
        self,
        *,
        collection_id: str | None = None,
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        stats = client.contents.get_progression_stats(
            collection_id="01965f7a-0000-7000-8000-000000000014",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        print(f"{stats.completed}/{stats.total} completed")
        ```

        Example response:
        ```python
        CollectionProgressionStats(total=12, completed=7)
        ```
        """
        params = {"collectionId": collection_id} if collection_id else None
        data = self._get_http(workspace_id).get(
            "/api/v1/progressions/stats", params=params
        )
        if data is None:
            return CollectionProgressionStats()
        return CollectionProgressionStats.model_validate(data)

    # -- V2 --

    def get_v2(self, content_id: str, *, workspace_id: str) -> ContentV2:
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        content = client.contents.get_v2(
            "01965f7a-0000-7000-8000-000000000005",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = self._get_http(workspace_id).get(f"/api/v2/contents/{content_id}")
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
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        for content in client.contents.filter_all(
            hub_profile_id,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        ):
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
                workspace_id=workspace_id,
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
        workspace_id: str,
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
        client = SRGClient(api_keys=["srgplus_your_key"])
        for content in client.contents.search_all(
            hub_profile_id,
            search="intro",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        ):
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
            workspace_id=workspace_id,
        )


class AsyncContentsResource:
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
        privacy: ContentPrivacy = "Preview",
        details: str | None = None,
        url: str | None = None,
        main_asset_id: str | None = None,
        cover_image: str | Path | None = None,
        cover: Any | None = None,  # noqa: ANN401
        channels: list[str | ContentChannelUpsert] | None = None,
        context: list[Any] | None = None,
        categories: list[Any] | None = None,
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            content = await client.contents.create(
                name="Welcome to the Team",
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                privacy="Public",
                main_asset_id="01965f7a-0000-7000-8000-000000000006",
                cover_image="/path/to/cover.jpg",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        _upload_type = "application/octet-stream"

        if cover_image is not None and cover is None:
            _img_bytes, _served_type = await read_image_async(cover_image)
            cover = _make_image_upsert(_img_bytes, cover_image, _served_type)
            _upload_type = image_content_type(cover.extension, _served_type)

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
        data = await self._get_http(workspace_id).post("/api/v1/contents", json=body)
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            await _upload_cover_async(result, _img_bytes, _upload_type)

        if cover_image is not None:
            return await self.get(
                result.id, hub_profile_id=hub_profile_id, workspace_id=workspace_id
            )
        return result

    async def get(
        self,
        content_id: str,
        *,
        hub_profile_id: str | None = None,
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            content = await client.contents.get(
                "01965f7a-0000-7000-8000-000000000005",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = await self._get_http(workspace_id).get(
            f"/api/v1/contents/{content_id}", params=params
        )
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
        workspace_id: str,
    ) -> Content | ContentUploadSignedUrl:
        """
        Update a content item. Only the fields you pass are changed.

        Async counterpart of :meth:`ContentsResource.update`: sends
        ``PATCH /api/v1/contents/{id}`` with just the supplied fields, so the
        cover, main asset, channels, categories and action buttons are never
        wiped by an update that doesn't mention them. Lists you pass
        (``channels``, ``context``, ``categories``) replace the stored list.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or
        an ``http(s)://`` URL (no extension needed). **Manual mode** — pass
        ``cover`` to get back
        :class:`~srg.schemas.content.ContentUploadSignedUrl`.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            # Only the body changes; cover, channels and categories stay.
            await client.contents.update(
                "01965f7a-0000-7000-8000-000000000005",
                context=[{"$type": "Text", "content": "New caption"}],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        if hub_profile_id is None:
            hub_profile_id = (
                await self.get_v2(content_id, workspace_id=workspace_id)
            ).hub_profile_id

        _img_bytes: bytes | None = None
        _upload_type = "application/octet-stream"

        if cover_image is not None and cover is None:
            _img_bytes, _served_type = await read_image_async(cover_image)
            cover = _make_content_file_params(_img_bytes, cover_image, _served_type)
            if cover.image is not None:
                _upload_type = image_content_type(cover.image.extension, _served_type)

        body = _build_patch_body(
            name=name,
            privacy=privacy,
            details=details,
            url=url,
            main_asset_id=main_asset_id,
            cover=cover,
            channels=channels,
            context=context,
            categories=categories,
        )

        data = await self._get_http(workspace_id).patch(
            f"/api/v1/contents/{content_id}",
            json=body,
            params={"hubProfileId": hub_profile_id},
        )
        result = ContentUploadSignedUrl.model_validate(data)

        if _img_bytes is not None:
            await _upload_cover_async(result, _img_bytes, _upload_type)

        if cover_image is not None:
            return await self.get(
                content_id, hub_profile_id=hub_profile_id, workspace_id=workspace_id
            )
        return result

    async def set_cover_from_asset(
        self,
        content_id: str,
        asset_id: str,
        *,
        hub_profile_id: str | None = None,
        workspace_id: str,
    ) -> None:
        """Async counterpart of :meth:`ContentsResource.set_cover_from_asset`."""
        if hub_profile_id is None:
            hub_profile_id = (
                await self.get_v2(content_id, workspace_id=workspace_id)
            ).hub_profile_id
        await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/cover/from-asset",
            json={"coverAssetId": asset_id},
            params={"hubProfileId": hub_profile_id},
        )

    async def archive(self, content_id: str, *, workspace_id: str) -> None:
        """Archive a content item (reversible — see :meth:`restore`)."""
        await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/archive"
        )

    async def restore(self, content_id: str, *, workspace_id: str) -> None:
        """Restore a previously archived content item."""
        await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/restore"
        )

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
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            page = await client.contents.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=20,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = await self._get_http(workspace_id).post(
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
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            results = await client.contents.search(
                "01965f7a-0000-7000-8000-000000000002",
                search="welcome",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = await self._get_http(workspace_id).post(
            f"/api/v1/contents/{hub_profile_id}/search", json=body
        )
        return [ContentSearch.model_validate(item) for item in (data or [])]

    async def add_to_categories(
        self,
        content_id: str,
        *,
        channels_categories: list[ContentChannelUpsert],
        workspace_id: str,
    ) -> None:
        """
        Add a content item to one or more channel categories.

        Args:
            content_id: ID of the content item.
            channels_categories: Channel and category placements to add the
                content to.

        Example:
        ```python
        from srg.schemas.content import ContentChannelUpsert

        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.add_to_categories(
                "01965f7a-0000-7000-8000-000000000005",
                channels_categories=[
                    ContentChannelUpsert(
                        channel_id="01965f7a-0000-7000-8000-000000000003",
                        category_ids=["01965f7a-0000-7000-8000-000000000004"],
                    )
                ],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body = {
            "contentId": content_id,
            "channelsCategories": _ser_list(channels_categories),
        }
        await self._get_http(workspace_id).put(
            "/api/v1/contents/channels/add", json=body
        )

    async def remove_from_categories(
        self,
        content_id: str,
        *,
        channels_categories: list[ContentChannelUpsert],
        workspace_id: str,
    ) -> None:
        """
        Remove a content item from one or more channel categories.

        The content item itself is not deleted.

        Args:
            content_id: ID of the content item.
            channels_categories: Channel and category placements to remove
                the content from.

        Example:
        ```python
        from srg.schemas.content import ContentChannelUpsert

        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.remove_from_categories(
                "01965f7a-0000-7000-8000-000000000005",
                channels_categories=[
                    ContentChannelUpsert(
                        channel_id="01965f7a-0000-7000-8000-000000000003",
                        category_ids=["01965f7a-0000-7000-8000-000000000004"],
                    )
                ],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body = {
            "contentId": content_id,
            "channelsCategories": _ser_list(channels_categories),
        }
        await self._get_http(workspace_id).put(
            "/api/v1/contents/channels/categories/delete", json=body
        )

    async def move(
        self,
        content_id: str,
        *,
        channel_id: str,
        category_id: str,
        section_id: str,
        workspace_id: str,
    ) -> None:
        """
        Move a content item to a different channel category.

        Args:
            content_id: ID of the content item.
            channel_id: ID of the channel containing the target category.
            category_id: ID of the destination category.
            section_id: ID of the destination section within the category.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.move(
                "01965f7a-0000-7000-8000-000000000005",
                channel_id="01965f7a-0000-7000-8000-000000000003",
                category_id="01965f7a-0000-7000-8000-000000000013",
                section_id="01965f7a-0000-7000-8000-000000000011",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        body = {
            "channelId": channel_id,
            "categoryId": category_id,
            "sectionId": section_id,
        }
        await self._get_http(workspace_id).put(
            f"/api/v1/contents/{content_id}/channels/categories/move-to", json=body
        )

    async def create_section(
        self,
        content_id: str,
        category_name: str,
        *,
        name: str,
        workspace_id: str,
    ) -> CreatedSection:
        """
        Create a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            name: Display name of the new section.

        Returns:
            CreatedSection with the ID of the newly created section.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            result = await client.contents.create_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                name="Day 1",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
            print(result.id)
        ```
        """
        data = await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}/sections",
            json={"name": name},
        )
        return CreatedSection.model_validate(data)

    async def update_section(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        name: str,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the name of a section in a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            section_id: ID of the section to update.
            name: New display name.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.update_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                "01965f7a-0000-7000-8000-000000000011",
                name="Day 1 (Updated)",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).put(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}",
            json={"name": name},
        )

    async def delete_section(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        workspace_id: str,
    ) -> None:
        """
        Delete a section from a content item's category.

        Args:
            content_id: ID of the collection content item.
            category_name: Name slug of the category.
            section_id: ID of the section to delete.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.delete_section(
                "01965f7a-0000-7000-8000-000000000005",
                "week-1",
                "01965f7a-0000-7000-8000-000000000011",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/contents/{content_id}/{category_name}/sections/{section_id}"
        )

    # -- Subcontent (collection child items) --

    async def add_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        subcontent_ids: list[str],
        workspace_id: str,
    ) -> None:
        """
        Add content items as subcontent inside a collection section.

        After calling this the content becomes a Collection
        (``IsCollection()`` returns true on the server side).

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section to add subcontent into.
            subcontent_ids: IDs of the content items to nest inside the collection.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.add_subcontent(
                "01965f7a-0000-7000-8000-000000000005",
                "Content",
                "01965f7a-0000-7000-8000-000000000011",
                subcontent_ids=[
                    "01965f7a-0000-7000-8000-000000000020",
                    "01965f7a-0000-7000-8000-000000000021",
                ],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}/{section_id}/references",
            json={"referenceIds": subcontent_ids},
        )

    async def get_subcontent(
        self,
        content_id: str,
        category_name: str,
        *,
        page_size: int,
        cursor: str | None = None,
        order: str = "Asc",
        workspace_id: str,
    ) -> CursorPagedList[SubcontentItem]:
        """
        Get paginated subcontent (child items) of a collection.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            page_size: Maximum number of items to return per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            order: Sort order — ``"Asc"`` (default) or ``"Desc"``.

        Returns:
            CursorPagedList[SubcontentItem] with items and an optional cursor
            for the next page.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            page = await client.contents.get_subcontent(
                "01965f7a-0000-7000-8000-000000000005",
                "Content",
                page_size=20,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
            for item in page.items:
                print(item.id, item.name)
        ```
        """
        params: dict = {"pageSize": page_size, "order": order}
        if cursor is not None:
            params["cursor"] = cursor
        data = await self._get_http(workspace_id).get(
            f"/api/v1/contents/{content_id}/{category_name}/references",
            params=params,
        )
        items = [SubcontentItem.model_validate(i) for i in (data.get("items") or [])]
        return CursorPagedList[SubcontentItem](items=items, cursor=data.get("cursor"))

    async def delete_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        subcontent_id: str,
        workspace_id: str,
    ) -> None:
        """
        Remove a subcontent item from a collection section.

        The subcontent item itself is not deleted — only the link is removed.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section containing the subcontent.
            subcontent_id: ID of the subcontent item to remove.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.delete_subcontent(
                "01965f7a-0000-7000-8000-000000000005",
                "Content",
                "01965f7a-0000-7000-8000-000000000011",
                "01965f7a-0000-7000-8000-000000000020",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).delete(
            f"/api/v1/contents/{content_id}/{category_name}"
            f"/{section_id}/references/{subcontent_id}",
        )

    async def move_subcontent(
        self,
        content_id: str,
        category_name: str,
        section_id: str,
        *,
        subcontent_id: str,
        previous_subcontent_id: str | None = None,
        workspace_id: str,
    ) -> None:
        """
        Reorder a subcontent item within a collection section.

        Moves ``subcontent_id`` to the position immediately after
        ``previous_subcontent_id``. Pass ``None`` to move it to the first
        position.

        Args:
            content_id: ID of the collection content item.
            category_name: Category name — ``"Content"`` or ``"Asset"``.
            section_id: ID of the section containing the subcontent.
            subcontent_id: ID of the subcontent item to move.
            previous_subcontent_id: ID of the item that should precede the
                moved item. ``None`` moves it to the first position.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.move_subcontent(
                "01965f7a-0000-7000-8000-000000000005",
                "Content",
                "01965f7a-0000-7000-8000-000000000011",
                subcontent_id="01965f7a-0000-7000-8000-000000000021",
                previous_subcontent_id="01965f7a-0000-7000-8000-000000000020",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        await self._get_http(workspace_id).post(
            f"/api/v1/contents/{content_id}/{category_name}"
            f"/{section_id}/references/move",
            json={
                "referenceId": subcontent_id,
                "previousReferenceId": previous_subcontent_id,
            },
        )

    async def patch_content_progression(
        self,
        content_id: str,
        *,
        status: ProgressionStatus,
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            progression = await client.contents.patch_content_progression(
                "01965f7a-0000-7000-8000-000000000005",
                status="Completed",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        ContentProgression(status="Completed")
        ```
        """
        data = await self._get_http(workspace_id).patch(
            f"/api/v1/progressions/contents/{content_id}",
            json={"status": status},
        )
        if data is None:
            return ContentProgression()
        return ContentProgression.model_validate(data)

    async def patch_media_progression(
        self,
        media_id: str,
        *,
        last_watched_time: int,
        workspace_id: str,
    ) -> dict | None:
        """
        Update the current user's last watched position in a media asset.

        Args:
            media_id: ID of the media asset.
            last_watched_time: Playback position in seconds.

        Returns:
            ``None`` if no body is returned, otherwise a raw response dict.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            await client.contents.patch_media_progression(
                "01965f7a-0000-7000-8000-000000000006",
                last_watched_time=95,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```
        """
        return await self._get_http(workspace_id).patch(
            f"/api/v1/progressions/medias/{media_id}",
            json={"lastWatchedTime": last_watched_time},
        )

    async def get_progression_stats(
        self,
        *,
        collection_id: str | None = None,
        workspace_id: str,
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            stats = await client.contents.get_progression_stats(
                collection_id="01965f7a-0000-7000-8000-000000000014",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        CollectionProgressionStats(total=12, completed=7)
        ```
        """
        params = {"collectionId": collection_id} if collection_id else None
        data = await self._get_http(workspace_id).get(
            "/api/v1/progressions/stats", params=params
        )
        if data is None:
            return CollectionProgressionStats()
        return CollectionProgressionStats.model_validate(data)

    # -- V2 --

    async def get_v2(self, content_id: str, *, workspace_id: str) -> ContentV2:
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
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            content = await client.contents.get_v2(
                "01965f7a-0000-7000-8000-000000000005",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
        data = await self._get_http(workspace_id).get(f"/api/v2/contents/{content_id}")
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
        workspace_id: str,
    ) -> AsyncIterator[ContentSearch]:
        """
        Async-iterate over all content items for a hub profile across all pages.

        Wraps :meth:`filter` and handles cursor-based pagination automatically.
        Yields individual :class:`~srg.schemas.content.ContentSearch` items.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            async for content in client.contents.filter_all(
                hub_profile_id,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            ):
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
                workspace_id=workspace_id,
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
        workspace_id: str,
    ) -> AsyncIterator[ContentSearch]:
        """
        Async-iterate over all content search results.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            async for content in client.contents.search_all(
                hub_profile_id,
                search="intro",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
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
            workspace_id=workspace_id,
        ):
            yield item
