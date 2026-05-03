from collections.abc import AsyncIterator, Iterator
from pathlib import Path

from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg._upload import (
    upload_to_signed_url,
    upload_to_signed_url_async,
)
from srg.exceptions import SRGError
from srg.schemas.asset import (
    AnyAssetCreate,
    AnyAssetResponse,
    AssetSearch,
    AssetUploadSignedUrl,
    parse_asset_response,
)
from srg.schemas.common import ContentFileUploadParameters, CursorPagedList


def _build_filter_body(
    page_size: int,
    only_archived: bool,
    exclude_collections: list[str] | None,
    exclude_assets: list[str] | None,
    types: list[str] | None,
    cursor: str | None,
) -> dict:
    body: dict = {
        "pageSize": page_size,
        "onlyArchived": only_archived,
        "excludeCollections": exclude_collections or [],
        "excludeAssets": exclude_assets or [],
    }
    if types:
        body["type"] = types
    if cursor is not None:
        body["cursor"] = cursor
    return body


def _build_search_body(
    search: str,
    types: list[str] | None,
    exclude_categories: list[str] | None,
    exclude_collections: list[str] | None,
    exclude_medias: list[str] | None,
) -> dict:
    body: dict = {"search": search}
    if types is not None:
        body["type"] = types
    if exclude_categories is not None:
        body["excludeCategories"] = exclude_categories
    if exclude_collections is not None:
        body["excludeCollections"] = exclude_collections
    if exclude_medias is not None:
        body["excludeMedias"] = exclude_medias
    return body


class AssetsResource:
    def __init__(self, registry: dict[str, SyncHTTPClient]) -> None:
        self._registry = registry

    def _resolve_workspace_id(self, workspace_id: str) -> str:
        if workspace_id not in self._registry:
            raise SRGError(f"No API key registered for workspace '{workspace_id}'")
        return workspace_id

    def _get_http(self, workspace_id: str) -> SyncHTTPClient:
        return self._registry[self._resolve_workspace_id(workspace_id)]

    def create(
        self, *, hub_profile_id: str, asset: AnyAssetCreate, workspace_id: str
    ) -> AnyAssetResponse:
        """
        Create a new asset for a hub profile.

        Creates an asset of the specified type and associates it with the
        given hub profile. After creation the asset is in a
        ``"pending_upload"`` state — upload the actual file to the storage
        backend before using it in content.

        Use one of the typed create models to specify the asset kind:
        ``MediaAssetCreate`` (video), ``EmbedAssetCreate`` (external embed),
        ``FileAssetCreate``, ``ImageAssetCreate``, or ``VideoAssetCreate``.

        Args:
            hub_profile_id: ID of the hub profile to associate the asset with.
            asset: Asset creation payload. The ``$type`` discriminator field
                controls which concrete asset type is created.

        Returns:
            The created asset. The concrete type depends on the ``$type``
            field: ``Media``, ``Embed``, ``File``, ``ImageMedia``, or
            ``Video``.

        Example:
        ```python
        from sdk.schemas.asset import MediaAssetCreate

        client = SRGClient(api_keys=["srgplus_your_key"])
        asset = client.assets.create(
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            asset=MediaAssetCreate(
                name="Intro Video",
                duration_in_seconds=120.0,
                memory_size_in_bytes=52_428_800,
            ),
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video",
            hls_stream_url=None,
            status="pending_upload",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52428800,
            cover=None,
        )
        ```
        """
        data = self._get_http(workspace_id).post(
            "/api/v1/assets",
            json={
                "hubProfileId": hub_profile_id,
                "asset": asset.model_dump(by_alias=True, exclude_none=True),
            },
        )
        return parse_asset_response(data)

    def create_batch(
        self,
        *,
        hub_profile_id: str,
        assets: list[AnyAssetCreate],
        workspace_id: str,
    ) -> list[AnyAssetResponse]:
        """
        Create multiple assets for a hub profile in a single request.

        Batch-creates assets and associates them all with the given hub
        profile. Equivalent to calling ``create`` multiple times but in
        a single API round-trip.

        Args:
            hub_profile_id: ID of the hub profile to associate all assets with.
            assets: List of asset creation payloads. Each entry can be a
                different asset type.

        Returns:
            List of created assets in the same order as the input list.
            Each item's concrete type is determined by its ``$type`` field.

        Example:
        ```python
        from sdk.schemas.asset import FileAssetCreate, ImageAssetCreate

        client = SRGClient(api_keys=["srgplus_your_key"])
        assets = client.assets.create_batch(
            hub_profile_id="01965f7a-0000-7000-8000-000000000002",
            assets=[
                FileAssetCreate(
                    name="Handbook.pdf",
                    extension="pdf",
                    memory_size_in_bytes=204_800,
                ),
                ImageAssetCreate(
                    name="Banner",
                    extension="png",
                    width=1920.0,
                    height=1080.0,
                    memory_size_in_bytes=512_000,
                ),
            ],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        [
            File(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Handbook.pdf",
                file_type="application/pdf",
                extension="pdf",
                memory_size_in_bytes=204800,
                url="https://cdn.srgplus.com/files/handbook.pdf",
                read_only=False,
                cover=None,
            ),
            ImageMedia(
                id="01965f7a-0000-7000-8000-000000000007",
                name="Banner",
                file_type="image/png",
                extension="png",
                memory_size_in_bytes=512000,
                url="https://cdn.srgplus.com/images/banner.png",
                read_only=False,
                width=1920.0,
                height=1080.0,
                cover=None,
            ),
        ]
        ```
        """
        data = self._get_http(workspace_id).post(
            "/api/v1/assets/batch",
            json={
                "hubProfileId": hub_profile_id,
                "assets": [
                    a.model_dump(by_alias=True, exclude_none=True) for a in assets
                ],
            },
        )
        return [parse_asset_response(item) for item in (data or [])]

    def get(self, asset_id: str, *, workspace_id: str) -> AnyAssetResponse:
        """
        Get an asset by ID.

        Retrieves the full details of a single asset. The returned object's
        concrete type depends on the asset's ``$type`` field.

        Args:
            asset_id: ID of the asset to retrieve.

        Returns:
            The asset. Concrete type is one of ``Media``, ``Embed``, ``File``,
            ``ImageMedia``, or ``Video`` based on ``$type``.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        asset = client.assets.get(
            "01965f7a-0000-7000-8000-000000000006",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video",
            hls_stream_url="https://stream.srgplus.com/hls/intro-video/playlist.m3u8",
            status="ready",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52428800,
            cover=AssetCover(
                width=1920.0,
                height=1080.0,
                extension="jpg",
                size=153600,
                modified="2025-06-01T10:00:00Z",
                urls=CoverUrls(
                    original="https://cdn.srgplus.com/covers/intro-video.jpg",
                    thumbnail_large=None,
                    thumbnail_small=None,
                    large=None,
                    blurred_large=None,
                    seo=None,
                ),
            ),
        )
        ```
        """
        data = self._get_http(workspace_id).get(f"/api/v1/assets/{asset_id}")
        return parse_asset_response(data)

    def update(
        self,
        asset_id: str,
        *,
        name: str,
        cover_image: str | Path | None = None,
        cover: ContentFileUploadParameters | None = None,
        read_only: bool = False,
        workspace_id: str,
    ) -> AnyAssetResponse | AssetUploadSignedUrl:
        """
        Update an asset's name, cover, and read-only flag.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image (including any S3
        metadata headers) and returns the updated asset.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.asset.AssetUploadSignedUrl` with a signed
        URL so you can upload the image yourself.

        Args:
            asset_id: ID of the asset to update.
            name: New display name for the asset.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            read_only: Whether to mark the asset as read-only. Defaults to
                False.

        Returns:
            The updated asset (concrete subtype of ``AnyAssetResponse``) when
            ``cover_image`` is provided (auto-upload mode).
            :class:`~srg.schemas.asset.AssetUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        asset = client.assets.update(
            "01965f7a-0000-7000-8000-000000000006",
            name="Intro Video (Final)",
            cover_image="/path/to/thumbnail.jpg",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        # asset is the updated Media/File/etc. with cover populated
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video (Final)",
            hls_stream_url="https://stream.srgplus.com/hls/intro-video/playlist.m3u8",
            status="ready",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52428800,
            cover=AssetCover(
                modified="2025-06-01T12:00:00Z",
                extension="jpg",
                urls=AssetCoverUrls(
                    original="https://cdn.srgplus.com/covers/intro-video.jpg",
                ),
            ),
        )
        ```
        """
        if cover_image is not None and cover is None:
            cover = ContentFileUploadParameters(generate_signed_url=True)

        body: dict = {"name": name, "readOnly": read_only}
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)
        data = self._get_http(workspace_id).put(f"/api/v1/assets/{asset_id}", json=body)
        result = AssetUploadSignedUrl.model_validate(data)

        if cover_image is not None and result.cover_signed_url is not None:
            upload_to_signed_url(
                result.cover_signed_url.url,
                cover_image,
                extra_headers=result.metadata_headers,
            )

        if cover_image is not None:
            return self.get(asset_id)
        return result

    def filter(
        self,
        hub_profile_id: str,
        *,
        page_size: int,
        cursor: str | None = None,
        only_archived: bool = False,
        exclude_collections: list[str] | None = None,
        exclude_assets: list[str] | None = None,
        types: list[str] | None = None,
        workspace_id: str,
    ) -> CursorPagedList[AssetSearch]:
        """
        List assets for a hub profile with cursor-based pagination.

        Returns a page of asset summaries for the given hub profile. Supports
        filtering by archive status, asset type, and exclusion lists. Pass the
        returned ``cursor`` to subsequent calls to retrieve the next page.

        Use ``paginate()`` from ``sdk.schemas.common`` to iterate all pages
        automatically.

        Args:
            hub_profile_id: ID of the hub profile to list assets for.
            page_size: Maximum number of assets to return per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            only_archived: If True, return only archived assets. Defaults to
                False.
            exclude_collections: Collection IDs whose assets should be
                excluded from results.
            exclude_assets: Asset IDs to exclude from results.
            types: Asset types to include (e.g. ``["Media", "File"]``). All
                types are returned if omitted.

        Returns:
            CursorPagedList[AssetSearch] with a list of asset summaries and
            an optional cursor for the next page.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        page = client.assets.filter(
            "01965f7a-0000-7000-8000-000000000002",
            page_size=20,
            types=["Media"],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        for asset in page.items:
            print(asset.name)

        # Or use paginate() to iterate all pages:
        from sdk import paginate

        for asset in paginate(
            lambda cursor: client.assets.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=50,
                cursor=cursor,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ):
            print(asset.name)
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                AssetSearch(
                    id="01965f7a-0000-7000-8000-000000000006",
                    name="Intro Video",
                    type="Media",
                    cover=None,
                    status="ready",
                ),
                AssetSearch(
                    id="01965f7a-0000-7000-8000-000000000007",
                    name="Banner",
                    type="Image",
                    cover=None,
                    status=None,
                ),
            ],
            cursor="eyJpZCI6IjAxOTY1ZjdhIn0",
        )
        ```
        """
        body = _build_filter_body(
            page_size, only_archived, exclude_collections, exclude_assets, types, cursor
        )
        data = self._get_http(workspace_id).post(
            f"/api/v1/assets/{hub_profile_id}/filter/", json=body
        )
        result = CursorPagedList[AssetSearch].model_validate(data)
        result.items = [
            AssetSearch.model_validate(item) for item in (data.get("items") or [])
        ]
        return result

    def search(
        self,
        hub_profile_id: str,
        *,
        search: str,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_medias: list[str] | None = None,
        workspace_id: str,
    ) -> list[AssetSearch]:
        """
        Search assets in a hub profile by name or keyword.

        Performs a text search across asset names in the hub profile.
        Returns a flat list (not paginated) — use ``filter`` for paginated
        browsing.

        Args:
            hub_profile_id: ID of the hub profile to search within.
            search: Search query string (matched against asset names).
            types: Asset types to include (e.g. ``["Media", "File"]``). All
                types if omitted.
            exclude_categories: Category IDs to exclude from results.
            exclude_collections: Collection IDs to exclude from results.
            exclude_medias: Media asset IDs to exclude from results.

        Returns:
            List of AssetSearch objects matching the query.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        results = client.assets.search(
            "01965f7a-0000-7000-8000-000000000002",
            search="intro",
            types=["Media"],
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        )
        ```

        Example response:
        ```python
        [
            AssetSearch(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Intro Video",
                type="Media",
                cover=None,
                status="ready",
            ),
        ]
        ```
        """
        body = _build_search_body(
            search, types, exclude_categories, exclude_collections, exclude_medias
        )
        data = self._get_http(workspace_id).post(
            f"/api/v1/assets/{hub_profile_id}/search", json=body
        )
        return [AssetSearch.model_validate(item) for item in (data or [])]

    def filter_all(
        self,
        hub_profile_id: str,
        *,
        page_size: int = 50,
        only_archived: bool = False,
        exclude_collections: list[str] | None = None,
        exclude_assets: list[str] | None = None,
        types: list[str] | None = None,
        workspace_id: str,
    ) -> Iterator[AssetSearch]:
        """
        Iterate over all assets for a hub profile across all pages.

        Wraps :meth:`filter` and handles cursor-based pagination automatically.
        Yields individual :class:`~srg.schemas.asset.AssetSearch` items.

        Args:
            hub_profile_id: ID of the hub profile.
            page_size: Items per page. Defaults to 50.
            only_archived: If True, return only archived assets.
            exclude_collections: Collection IDs to exclude.
            exclude_assets: Asset IDs to exclude.
            types: Asset types to include (e.g. ``["Media", "File"]``).

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        for asset in client.assets.filter_all(
            hub_profile_id,
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        ):
            print(asset.name)
        ```
        """
        cursor: str | None = None
        while True:
            page = self.filter(
                hub_profile_id,
                page_size=page_size,
                cursor=cursor,
                only_archived=only_archived,
                exclude_collections=exclude_collections,
                exclude_assets=exclude_assets,
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
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_medias: list[str] | None = None,
        workspace_id: str,
    ) -> Iterator[AssetSearch]:
        """
        Iterate over all asset search results as an iterator.

        Wraps :meth:`search` and returns results as a lazy iterator for a
        consistent interface with :meth:`filter_all`.

        Args:
            hub_profile_id: ID of the hub profile.
            search: Search query string.
            types: Asset types to include.
            exclude_categories: Category IDs to exclude.
            exclude_collections: Collection IDs to exclude.
            exclude_medias: Media asset IDs to exclude.

        Example:
        ```python
        client = SRGClient(api_keys=["srgplus_your_key"])
        for asset in client.assets.search_all(
            hub_profile_id,
            search="intro",
            workspace_id="01965f7a-0000-7000-8000-000000000001",
        ):
            print(asset.name)
        ```
        """
        yield from self.search(
            hub_profile_id,
            search=search,
            types=types,
            exclude_categories=exclude_categories,
            exclude_collections=exclude_collections,
            exclude_medias=exclude_medias,
            workspace_id=workspace_id,
        )


class AsyncAssetsResource:
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
        hub_profile_id: str,
        asset: AnyAssetCreate,
        workspace_id: str,
    ) -> AnyAssetResponse:
        """
        Create a new asset for a hub profile.

        Creates an asset of the specified type and associates it with the
        given hub profile. After creation the asset is in a
        ``"pending_upload"`` state — upload the actual file to the storage
        backend before using it in content.

        Args:
            hub_profile_id: ID of the hub profile to associate the asset with.
            asset: Asset creation payload. Use one of the typed create models:
                ``MediaAssetCreate``, ``EmbedAssetCreate``, ``FileAssetCreate``,
                ``ImageAssetCreate``, or ``VideoAssetCreate``.

        Returns:
            The created asset. Concrete type is one of ``Media``, ``Embed``,
            ``File``, ``ImageMedia``, or ``Video``.

        Example:
        ```python
        from sdk.schemas.asset import MediaAssetCreate

        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            asset = await client.assets.create(
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                asset=MediaAssetCreate(
                    name="Intro Video",
                    duration_in_seconds=120.0,
                    memory_size_in_bytes=52_428_800,
                ),
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video",
            hls_stream_url=None,
            status="pending_upload",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52428800,
            cover=None,
        )
        ```
        """
        data = await self._get_http(workspace_id).post(
            "/api/v1/assets",
            json={
                "hubProfileId": hub_profile_id,
                "asset": asset.model_dump(by_alias=True, exclude_none=True),
            },
        )
        return parse_asset_response(data)

    async def create_batch(
        self,
        *,
        hub_profile_id: str,
        assets: list[AnyAssetCreate],
        workspace_id: str,
    ) -> list[AnyAssetResponse]:
        """
        Create multiple assets for a hub profile in a single request.

        Batch-creates assets and associates them all with the given hub
        profile. Equivalent to calling ``create`` multiple times but in
        a single API round-trip.

        Args:
            hub_profile_id: ID of the hub profile to associate all assets with.
            assets: List of asset creation payloads.

        Returns:
            List of created assets in the same order as the input list.

        Example:
        ```python
        from sdk.schemas.asset import FileAssetCreate

        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            assets = await client.assets.create_batch(
                hub_profile_id="01965f7a-0000-7000-8000-000000000002",
                assets=[
                    FileAssetCreate(
                        name="Handbook.pdf",
                        extension="pdf",
                        memory_size_in_bytes=204_800,
                    ),
                ],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        [
            File(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Handbook.pdf",
                file_type="application/pdf",
                extension="pdf",
                memory_size_in_bytes=204800,
                url="https://cdn.srgplus.com/files/handbook.pdf",
                read_only=False,
                cover=None,
            ),
        ]
        ```
        """
        data = await self._get_http(workspace_id).post(
            "/api/v1/assets/batch",
            json={
                "hubProfileId": hub_profile_id,
                "assets": [
                    a.model_dump(by_alias=True, exclude_none=True) for a in assets
                ],
            },
        )
        return [parse_asset_response(item) for item in (data or [])]

    async def get(self, asset_id: str, *, workspace_id: str) -> AnyAssetResponse:
        """
        Get an asset by ID.

        Retrieves the full details of a single asset. The returned object's
        concrete type depends on the asset's ``$type`` field.

        Args:
            asset_id: ID of the asset to retrieve.

        Returns:
            The asset. Concrete type is one of ``Media``, ``Embed``, ``File``,
            ``ImageMedia``, or ``Video`` based on ``$type``.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            asset = await client.assets.get(
                "01965f7a-0000-7000-8000-000000000006",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video",
            hls_stream_url="https://stream.srgplus.com/hls/intro-video/playlist.m3u8",
            status="ready",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52428800,
            cover=None,
        )
        ```
        """
        data = await self._get_http(workspace_id).get(f"/api/v1/assets/{asset_id}")
        return parse_asset_response(data)

    async def update(
        self,
        asset_id: str,
        *,
        name: str,
        cover_image: str | Path | None = None,
        cover: ContentFileUploadParameters | None = None,
        read_only: bool = False,
        workspace_id: str,
    ) -> AnyAssetResponse | AssetUploadSignedUrl:
        """
        Update an asset's name, cover, and read-only flag.

        **Auto-upload mode** — pass ``cover_image`` as a local file path or an
        ``http(s)://`` URL. The SDK uploads the image and returns the updated
        asset.

        **Manual mode** — pass ``cover`` as
        :class:`~srg.schemas.common.ContentFileUploadParameters`. The API
        returns :class:`~srg.schemas.asset.AssetUploadSignedUrl` with a signed
        URL so you can upload the image yourself.

        Args:
            asset_id: ID of the asset to update.
            name: New display name for the asset.
            cover_image: Local path or ``http(s)://`` URL of the new cover
                image. Triggers auto-upload.
            cover: Cover image upload parameters (manual mode).
            read_only: Whether to mark the asset as read-only. Defaults to
                False.

        Returns:
            The updated asset when ``cover_image`` is provided (auto-upload
            mode). :class:`~srg.schemas.asset.AssetUploadSignedUrl` otherwise
            (manual mode).

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            asset = await client.assets.update(
                "01965f7a-0000-7000-8000-000000000006",
                name="Intro Video (Final)",
                cover_image="/path/to/thumbnail.jpg",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        Media(
            id="01965f7a-0000-7000-8000-000000000006",
            name="Intro Video (Final)",
            status="ready",
            cover=AssetCover(
                extension="jpg",
                urls=AssetCoverUrls(
                    original="https://cdn.srgplus.com/covers/intro-video.jpg",
                ),
            ),
        )
        ```
        """
        if cover_image is not None and cover is None:
            cover = ContentFileUploadParameters(generate_signed_url=True)

        body: dict = {"name": name, "readOnly": read_only}
        if cover is not None:
            body["cover"] = cover.model_dump(by_alias=True, exclude_none=True)

        data = await self._get_http(workspace_id).put(
            f"/api/v1/assets/{asset_id}", json=body
        )
        result = AssetUploadSignedUrl.model_validate(data)

        if cover_image is not None and result.cover_signed_url is not None:
            await upload_to_signed_url_async(
                result.cover_signed_url.url,
                cover_image,
                extra_headers=result.metadata_headers,
            )

        if cover_image is not None:
            return await self.get(asset_id)
        return result

    async def filter(
        self,
        hub_profile_id: str,
        *,
        page_size: int,
        cursor: str | None = None,
        only_archived: bool = False,
        exclude_collections: list[str] | None = None,
        exclude_assets: list[str] | None = None,
        types: list[str] | None = None,
        workspace_id: str,
    ) -> CursorPagedList[AssetSearch]:
        """
        List assets for a hub profile with cursor-based pagination.

        Returns a page of asset summaries for the given hub profile. Pass the
        returned ``cursor`` to subsequent calls to retrieve the next page.

        Args:
            hub_profile_id: ID of the hub profile to list assets for.
            page_size: Maximum number of assets to return per page.
            cursor: Opaque cursor from the previous response. Omit for the
                first page.
            only_archived: If True, return only archived assets. Defaults to
                False.
            exclude_collections: Collection IDs whose assets should be excluded.
            exclude_assets: Asset IDs to exclude from results.
            types: Asset types to include (e.g. ``["Media", "File"]``). All
                types if omitted.

        Returns:
            CursorPagedList[AssetSearch] with asset summaries and an optional
            cursor for the next page.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            page = await client.assets.filter(
                "01965f7a-0000-7000-8000-000000000002",
                page_size=20,
                types=["Media"],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        CursorPagedList(
            items=[
                AssetSearch(
                    id="01965f7a-0000-7000-8000-000000000006",
                    name="Intro Video",
                    type="Media",
                    cover=None,
                    status="ready",
                ),
            ],
            cursor="eyJpZCI6IjAxOTY1ZjdhIn0",
        )
        ```
        """
        body = _build_filter_body(
            page_size, only_archived, exclude_collections, exclude_assets, types, cursor
        )
        data = await self._get_http(workspace_id).post(
            f"/api/v1/assets/{hub_profile_id}/filter", json=body
        )
        result = CursorPagedList[AssetSearch].model_validate(data)
        result.items = [
            AssetSearch.model_validate(item) for item in (data.get("items") or [])
        ]
        return result

    async def search(
        self,
        hub_profile_id: str,
        *,
        search: str,
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_medias: list[str] | None = None,
        workspace_id: str,
    ) -> list[AssetSearch]:
        """
        Search assets in a hub profile by name or keyword.

        Performs a text search across asset names in the hub profile. Returns
        a flat list — use ``filter`` for paginated browsing.

        Args:
            hub_profile_id: ID of the hub profile to search within.
            search: Search query string (matched against asset names).
            types: Asset types to include (e.g. ``["Media", "File"]``). All
                types if omitted.
            exclude_categories: Category IDs to exclude from results.
            exclude_collections: Collection IDs to exclude from results.
            exclude_medias: Media asset IDs to exclude from results.

        Returns:
            List of AssetSearch objects matching the query.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            results = await client.assets.search(
                "01965f7a-0000-7000-8000-000000000002",
                search="intro",
                types=["Media"],
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            )
        ```

        Example response:
        ```python
        [
            AssetSearch(
                id="01965f7a-0000-7000-8000-000000000006",
                name="Intro Video",
                type="Media",
                cover=None,
                status="ready",
            ),
        ]
        ```
        """
        body = _build_search_body(
            search, types, exclude_categories, exclude_collections, exclude_medias
        )
        data = await self._get_http(workspace_id).post(
            f"/api/v1/assets/{hub_profile_id}/search", json=body
        )
        return [AssetSearch.model_validate(item) for item in (data or [])]

    async def filter_all(
        self,
        hub_profile_id: str,
        *,
        page_size: int = 50,
        only_archived: bool = False,
        exclude_collections: list[str] | None = None,
        exclude_assets: list[str] | None = None,
        types: list[str] | None = None,
        workspace_id: str,
    ) -> AsyncIterator[AssetSearch]:
        """
        Async-iterate over all assets for a hub profile across all pages.

        Wraps :meth:`filter` and handles cursor-based pagination automatically.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            async for asset in client.assets.filter_all(
                hub_profile_id,
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            ):
                print(asset.name)
        ```
        """
        cursor: str | None = None
        while True:
            page = await self.filter(
                hub_profile_id,
                page_size=page_size,
                cursor=cursor,
                only_archived=only_archived,
                exclude_collections=exclude_collections,
                exclude_assets=exclude_assets,
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
        types: list[str] | None = None,
        exclude_categories: list[str] | None = None,
        exclude_collections: list[str] | None = None,
        exclude_medias: list[str] | None = None,
        workspace_id: str,
    ) -> AsyncIterator[AssetSearch]:
        """
        Async-iterate over all asset search results.

        Example:
        ```python
        async with AsyncSRGClient(api_keys=["srgplus_your_key"]) as client:
            async for asset in client.assets.search_all(
                hub_profile_id,
                search="intro",
                workspace_id="01965f7a-0000-7000-8000-000000000001",
            ):
                print(asset.name)
        ```
        """
        for item in await self.search(
            hub_profile_id,
            search=search,
            types=types,
            exclude_categories=exclude_categories,
            exclude_collections=exclude_collections,
            exclude_medias=exclude_medias,
            workspace_id=workspace_id,
        ):
            yield item
