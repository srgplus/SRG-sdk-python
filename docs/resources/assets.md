<a id="srg.resources.assets"></a>

# srg.resources.assets

<a id="srg.resources.assets.AssetsResource"></a>

## AssetsResource Objects

```python
class AssetsResource()
```

<a id="srg.resources.assets.AssetsResource.create"></a>

#### create

```python
def create(*, hub_profile_id: str, asset: AnyAssetCreate) -> AnyAssetResponse
```

Create a new asset for a hub profile.

Creates an asset of the specified type and associates it with the
given hub profile. After creation the asset is in a
``"pending_upload"`` state — upload the actual file to the storage
backend before using it in content.

Use one of the typed create models to specify the asset kind:
``MediaAssetCreate`` (video), ``EmbedAssetCreate`` (external embed),
``FileAssetCreate``, ``ImageAssetCreate``, or ``VideoAssetCreate``.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to associate the asset with.
- `asset` - Asset creation payload. The ``$type`` discriminator field
  controls which concrete asset type is created.
  

**Returns**:

  The created asset. The concrete type depends on the ``$type``
- `field` - ``Media``, ``Embed``, ``File``, ``ImageMedia``, or
  ``Video``.
  

**Example**:

```python
from sdk.schemas.asset import MediaAssetCreate

client = SRGClient(api_key="srgplus_your_key")
asset = client.assets.create(
    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
    asset=MediaAssetCreate(
        name="Intro Video",
        duration_in_seconds=120.0,
        memory_size_in_bytes=52_428_800,
    ),
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
<a id="srg.resources.assets.AssetsResource.create_batch"></a>

#### create\_batch

```python
def create_batch(
    *,
    hub_profile_id: str,
    assets: list[AnyAssetCreate]
) -> list[AnyAssetResponse]
```

Create multiple assets for a hub profile in a single request.

Batch-creates assets and associates them all with the given hub
profile. Equivalent to calling ``create`` multiple times but in
a single API round-trip.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to associate all assets with.
- `assets` - List of asset creation payloads. Each entry can be a
  different asset type.
  

**Returns**:

  List of created assets in the same order as the input list.
  Each item's concrete type is determined by its ``$type`` field.
  

**Example**:

```python
from sdk.schemas.asset import FileAssetCreate, ImageAssetCreate

client = SRGClient(api_key="srgplus_your_key")
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
<a id="srg.resources.assets.AssetsResource.get"></a>

#### get

```python
def get(asset_id: str) -> AnyAssetResponse
```

Get an asset by ID.

Retrieves the full details of a single asset. The returned object's
concrete type depends on the asset's ``$type`` field.

**Arguments**:

- `asset_id` - ID of the asset to retrieve.
  

**Returns**:

  The asset. Concrete type is one of ``Media``, ``Embed``, ``File``,
  ``ImageMedia``, or ``Video`` based on ``$type``.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
asset = client.assets.get("01965f7a-0000-7000-8000-000000000006")
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
<a id="srg.resources.assets.AssetsResource.update"></a>

#### update

```python
def update(
    asset_id: str,
    *,
    name: str,
    cover_image: str | Path | None = None,
    cover: ContentFileUploadParameters | None = None,
    read_only: bool = False
) -> AnyAssetResponse | AssetUploadSignedUrl
```

Update an asset's name, cover, and read-only flag.

**Auto-upload mode** — pass ``cover_image`` as a local file path or an
``http(s)://`` URL. The SDK uploads the image (including any S3
metadata headers) and returns the updated asset.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.ContentFileUploadParameters`. The API
returns :class:`~srg.schemas.asset.AssetUploadSignedUrl` with a signed
URL so you can upload the image yourself.

**Arguments**:

- `asset_id` - ID of the asset to update.
- `name` - New display name for the asset.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
- `read_only` - Whether to mark the asset as read-only. Defaults to
  False.
  

**Returns**:

  The updated asset (concrete subtype of ``AnyAssetResponse``) when
  ``cover_image`` is provided (auto-upload mode).
  :class:`~srg.schemas.asset.AssetUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
asset = client.assets.update(
    "01965f7a-0000-7000-8000-000000000006",
    name="Intro Video (Final)",
    cover_image="/path/to/thumbnail.jpg",
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

<a id="srg.resources.assets.AssetsResource.filter"></a>

#### filter

```python
def filter(
    hub_profile_id: str,
    *,
    page_size: int,
    cursor: str | None = None,
    only_archived: bool = False,
    exclude_collections: list[str] | None = None,
    exclude_assets: list[str] | None = None,
    types: list[str] | None = None
) -> CursorPagedList[AssetSearch]
```

List assets for a hub profile with cursor-based pagination.

Returns a page of asset summaries for the given hub profile. Supports
filtering by archive status, asset type, and exclusion lists. Pass the
returned ``cursor`` to subsequent calls to retrieve the next page.

Use ``paginate()`` from ``sdk.schemas.common`` to iterate all pages
automatically.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to list assets for.
- `page_size` - Maximum number of assets to return per page.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
- `only_archived` - If True, return only archived assets. Defaults to
  False.
- `exclude_collections` - Collection IDs whose assets should be
  excluded from results.
- `exclude_assets` - Asset IDs to exclude from results.
- `types` - Asset types to include (e.g. ``["Media", "File"]``). All
  types are returned if omitted.
  

**Returns**:

  CursorPagedList[AssetSearch] with a list of asset summaries and
  an optional cursor for the next page.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
page = client.assets.filter(
    "01965f7a-0000-7000-8000-000000000002",
    page_size=20,
    types=["Media"],
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

<a id="srg.resources.assets.AssetsResource.search"></a>

#### search

```python
def search(
    hub_profile_id: str,
    *,
    search: str,
    types: list[str] | None = None,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_medias: list[str] | None = None
) -> list[AssetSearch]
```

Search assets in a hub profile by name or keyword.

Performs a text search across asset names in the hub profile.
Returns a flat list (not paginated) — use ``filter`` for paginated
browsing.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to search within.
- `search` - Search query string (matched against asset names).
- `types` - Asset types to include (e.g. ``["Media", "File"]``). All
  types if omitted.
- `exclude_categories` - Category IDs to exclude from results.
- `exclude_collections` - Collection IDs to exclude from results.
- `exclude_medias` - Media asset IDs to exclude from results.
  

**Returns**:

  List of AssetSearch objects matching the query.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
results = client.assets.search(
    "01965f7a-0000-7000-8000-000000000002",
    search="intro",
    types=["Media"],
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
<a id="srg.resources.assets.AsyncAssetsResource"></a>

## AsyncAssetsResource Objects

```python
class AsyncAssetsResource()
```

<a id="srg.resources.assets.AsyncAssetsResource.create"></a>

#### create

```python
async def create(
    *,
    hub_profile_id: str,
    asset: AnyAssetCreate
) -> AnyAssetResponse
```

Create a new asset for a hub profile.

Creates an asset of the specified type and associates it with the
given hub profile. After creation the asset is in a
``"pending_upload"`` state — upload the actual file to the storage
backend before using it in content.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to associate the asset with.
- `asset` - Asset creation payload. Use one of the typed create models:
  ``MediaAssetCreate``, ``EmbedAssetCreate``, ``FileAssetCreate``,
  ``ImageAssetCreate``, or ``VideoAssetCreate``.
  

**Returns**:

  The created asset. Concrete type is one of ``Media``, ``Embed``,
  ``File``, ``ImageMedia``, or ``Video``.
  

**Example**:

```python
from sdk.schemas.asset import MediaAssetCreate

async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    asset = await client.assets.create(
        hub_profile_id="01965f7a-0000-7000-8000-000000000002",
        asset=MediaAssetCreate(
            name="Intro Video",
            duration_in_seconds=120.0,
            memory_size_in_bytes=52_428_800,
        ),
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
<a id="srg.resources.assets.AsyncAssetsResource.create_batch"></a>

#### create\_batch

```python
async def create_batch(
    *,
    hub_profile_id: str,
    assets: list[AnyAssetCreate]
) -> list[AnyAssetResponse]
```

Create multiple assets for a hub profile in a single request.

Batch-creates assets and associates them all with the given hub
profile. Equivalent to calling ``create`` multiple times but in
a single API round-trip.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to associate all assets with.
- `assets` - List of asset creation payloads.
  

**Returns**:

  List of created assets in the same order as the input list.
  

**Example**:

```python
from sdk.schemas.asset import FileAssetCreate

async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    assets = await client.assets.create_batch(
        hub_profile_id="01965f7a-0000-7000-8000-000000000002",
        assets=[
            FileAssetCreate(
                name="Handbook.pdf",
                extension="pdf",
                memory_size_in_bytes=204_800,
            ),
        ],
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
<a id="srg.resources.assets.AsyncAssetsResource.get"></a>

#### get

```python
async def get(asset_id: str) -> AnyAssetResponse
```

Get an asset by ID.

Retrieves the full details of a single asset. The returned object's
concrete type depends on the asset's ``$type`` field.

**Arguments**:

- `asset_id` - ID of the asset to retrieve.
  

**Returns**:

  The asset. Concrete type is one of ``Media``, ``Embed``, ``File``,
  ``ImageMedia``, or ``Video`` based on ``$type``.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    asset = await client.assets.get("01965f7a-0000-7000-8000-000000000006")
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
<a id="srg.resources.assets.AsyncAssetsResource.update"></a>

#### update

```python
async def update(
    asset_id: str,
    *,
    name: str,
    cover_image: str | Path | None = None,
    cover: ContentFileUploadParameters | None = None,
    read_only: bool = False
) -> AnyAssetResponse | AssetUploadSignedUrl
```

Update an asset's name, cover, and read-only flag.

**Auto-upload mode** — pass ``cover_image`` as a local file path or an
``http(s)://`` URL. The SDK uploads the image and returns the updated
asset.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.ContentFileUploadParameters`. The API
returns :class:`~srg.schemas.asset.AssetUploadSignedUrl` with a signed
URL so you can upload the image yourself.

**Arguments**:

- `asset_id` - ID of the asset to update.
- `name` - New display name for the asset.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
- `read_only` - Whether to mark the asset as read-only. Defaults to
  False.
  

**Returns**:

  The updated asset when ``cover_image`` is provided (auto-upload
  mode). :class:`~srg.schemas.asset.AssetUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    asset = await client.assets.update(
        "01965f7a-0000-7000-8000-000000000006",
        name="Intro Video (Final)",
        cover_image="/path/to/thumbnail.jpg",
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
<a id="srg.resources.assets.AsyncAssetsResource.filter"></a>

#### filter

```python
async def filter(
    hub_profile_id: str,
    *,
    page_size: int,
    cursor: str | None = None,
    only_archived: bool = False,
    exclude_collections: list[str] | None = None,
    exclude_assets: list[str] | None = None,
    types: list[str] | None = None
) -> CursorPagedList[AssetSearch]
```

List assets for a hub profile with cursor-based pagination.

Returns a page of asset summaries for the given hub profile. Pass the
returned ``cursor`` to subsequent calls to retrieve the next page.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to list assets for.
- `page_size` - Maximum number of assets to return per page.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
- `only_archived` - If True, return only archived assets. Defaults to
  False.
- `exclude_collections` - Collection IDs whose assets should be excluded.
- `exclude_assets` - Asset IDs to exclude from results.
- `types` - Asset types to include (e.g. ``["Media", "File"]``). All
  types if omitted.
  

**Returns**:

  CursorPagedList[AssetSearch] with asset summaries and an optional
  cursor for the next page.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    page = await client.assets.filter(
        "01965f7a-0000-7000-8000-000000000002",
        page_size=20,
        types=["Media"],
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
<a id="srg.resources.assets.AsyncAssetsResource.search"></a>

#### search

```python
async def search(
    hub_profile_id: str,
    *,
    search: str,
    types: list[str] | None = None,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_medias: list[str] | None = None
) -> list[AssetSearch]
```

Search assets in a hub profile by name or keyword.

Performs a text search across asset names in the hub profile. Returns
a flat list — use ``filter`` for paginated browsing.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to search within.
- `search` - Search query string (matched against asset names).
- `types` - Asset types to include (e.g. ``["Media", "File"]``). All
  types if omitted.
- `exclude_categories` - Category IDs to exclude from results.
- `exclude_collections` - Collection IDs to exclude from results.
- `exclude_medias` - Media asset IDs to exclude from results.
  

**Returns**:

  List of AssetSearch objects matching the query.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    results = await client.assets.search(
        "01965f7a-0000-7000-8000-000000000002",
        search="intro",
        types=["Media"],
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