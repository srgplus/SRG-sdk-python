<a id="srg.resources.contents"></a>

# srg.resources.contents

<a id="srg.resources.contents.ContentsResource"></a>

## ContentsResource Objects

```python
class ContentsResource()
```

<a id="srg.resources.contents.ContentsResource.create"></a>

#### create

```python
def create(
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
    categories: list[Any] | None = None
) -> Content | ContentUploadSignedUrl
```

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

**Arguments**:

- `name` - Display title of the content item.
- `hub_profile_id` - ID of the hub profile to create the content in.
- `privacy` - Visibility — ``"Preview"`` (default), ``"Private"``, or
  ``"Public"``.
- `details` - Optional body text / description.
- `url` - Optional external URL to associate with the content.
- `main_asset_id` - ID of the primary playable asset.
- `cover_image` - Local path or ``http(s)://`` URL of the cover image.
  Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
- `channels` - Channel and category placements for this content.
- `context` - Additional context objects.
- `categories` - Category assignments.
  

**Returns**:

  :class:`~srg.schemas.content.Content` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

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

<a id="srg.resources.contents.ContentsResource.get"></a>

#### get

```python
def get(content_id: str, *, hub_profile_id: str | None = None) -> Content
```

Get a content item by ID (v1).

Retrieves the full metadata for a content item, including its name,
description, cover, channel placements, and creation timestamps.

Use ``get_v2`` to also include the main playable asset and the
current user's progression.

**Arguments**:

- `content_id` - ID of the content item to retrieve.
- `hub_profile_id` - If provided, used to resolve access context for
  the request.
  

**Returns**:

  Content object with metadata and channel placement details.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.update"></a>

#### update

```python
def update(
    content_id: str,
    *,
    name: str,
    hub_profile_id: str | None = None,
    privacy: ContentPrivacy = "Preview",
    details: str | None = None,
    url: str | None = None,
    main_asset_id: str | None = None,
    cover_image: str | Path | None = None,
    cover: ContentFileUploadParameters | None = None,
    channels: list[str | ContentChannelUpsert] | None = None,
    context: list[Any] | None = None,
    categories: list[Any] | None = None
) -> Content | ContentUploadSignedUrl
```

Update a content item's metadata.

Replaces all metadata fields on the content item with the provided
values.

**Auto-upload mode** — pass ``cover_image`` as a local file path or
an ``http(s)://`` URL. The SDK uploads the image and returns the
updated :class:`~srg.schemas.content.Content`.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.ContentFileUploadParameters`. The API
returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
signed URL so you can upload the image yourself.

**Arguments**:

- `content_id` - ID of the content item to update.
- `name` - New display title.
- `hub_profile_id` - Hub profile that owns this content. Required by
  the API — pass the same value used when creating the content.
- `privacy` - New visibility level.
- `details` - New body text / description. Pass ``None`` to clear.
- `url` - New external URL. Pass ``None`` to clear.
- `main_asset_id` - New primary asset ID. Pass ``None`` to clear.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
- `channels` - New channel/category placements. Replaces existing.
- `context` - New context objects. Replaces existing.
- `categories` - New category assignments. Replaces existing.
  

**Returns**:

  :class:`~srg.schemas.content.Content` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
content = client.contents.update(
    "01965f7a-0000-7000-8000-000000000005",
    name="Welcome to the Team (v2)",
    privacy="Public",
    details="Updated onboarding guide.",
    cover_image="/path/to/new_cover.jpg",
)
# content is Content with cover already populated
```
  
  Example response:
```python
Content(
    id="01965f7a-0000-7000-8000-000000000005",
    name="Welcome to the Team (v2)",
    details="Updated onboarding guide.",
    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
    cover=ContentCover(
        urls=CoverUrls(
            original="https://cdn.srgplus.com/covers/welcome-v2.jpg",
        ),
        extension="jpg",
        modified="2025-06-01T12:00:00Z",
    ),
    channels=[],
)
```

<a id="srg.resources.contents.ContentsResource.filter"></a>

#### filter

```python
def filter(
    hub_profile_id: str,
    *,
    page_size: int,
    cursor: str | None = None,
    only_archived: bool = False,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_contents: list[str] | None = None,
    types: list[str] | None = None
) -> CursorPagedList[ContentSearch]
```

List content items for a hub profile with cursor-based pagination.

Returns a page of content summaries for the given hub profile. Supports
filtering by archive status, content type, and exclusion lists. Pass the
returned ``cursor`` to subsequent calls to retrieve the next page.

Use ``paginate()`` from ``sdk.schemas.common`` to iterate all pages
automatically.

**Arguments**:

- `hub_profile_id` - ID of the hub profile.
- `page_size` - Maximum number of items to return per page.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
- `only_archived` - If True, return only archived content. Defaults to
  False.
- `exclude_categories` - Category IDs whose content should be excluded.
- `exclude_collections` - Collection IDs to exclude.
- `exclude_contents` - Content IDs to exclude.
- `types` - Content types to include — ``"Content"``, ``"Collection"``,
  or both (default).
  

**Returns**:

  CursorPagedList[ContentSearch] with content summaries and an
  optional cursor for the next page.
  

**Example**:

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

<a id="srg.resources.contents.ContentsResource.search"></a>

#### search

```python
def search(
    hub_profile_id: str,
    *,
    search: str,
    only_archived: bool = False,
    types: list[str] | None = None,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_contents: list[str] | None = None
) -> list[ContentSearch]
```

Search content items in a hub profile by name or keyword.

Performs a text search across content names in the hub profile.
Returns a flat list (not paginated) — use ``filter`` for paginated
browsing.

**Arguments**:

- `hub_profile_id` - ID of the hub profile to search within.
- `search` - Search query string (matched against content names).
- `only_archived` - If True, search only archived content. Defaults
  to False.
- `types` - Content types to include. All types if omitted.
- `exclude_categories` - Category IDs to exclude.
- `exclude_collections` - Collection IDs to exclude.
- `exclude_contents` - Content IDs to exclude.
  

**Returns**:

  List of ContentSearch objects matching the query.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.add_to_categories"></a>

#### add\_to\_categories

```python
def add_to_categories(content_id: str, body: dict) -> None
```

Add a content item to one or more channel categories.

Places the content into the specified channel categories. The request
body schema follows the backend API format (see backend source for
details).

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body specifying which channel categories to add
  the content to.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.remove_from_categories"></a>

#### remove\_from\_categories

```python
def remove_from_categories(content_id: str, body: dict) -> None
```

Remove a content item from one or more channel categories.

Removes the content from the specified channel categories. The
content item itself is not deleted.

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body specifying which channel categories to remove
  the content from.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.move"></a>

#### move

```python
def move(content_id: str, body: dict) -> None
```

Move a content item to a different channel category.

Relocates the content from its current category position to a new
one within the same or a different channel.

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body specifying the source and destination
  category positions.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.create_section"></a>

#### create\_section

```python
def create_section(
    content_id: str,
    category_name: str,
    *,
    name: str
) -> None
```

Create a section in a content item's category.

Adds a named section to the specified category of a collection-type
content item. Sections group the nested content within a collection.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category to add the section to.
- `name` - Display name of the new section.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.contents.create_section(
    "01965f7a-0000-7000-8000-000000000005",
    "week-1",
    name="Day 1",
)
```
<a id="srg.resources.contents.ContentsResource.update_section"></a>

#### update\_section

```python
def update_section(
    content_id: str,
    category_name: str,
    section_id: str,
    *,
    name: str
) -> None
```

Update the name of a section in a content item's category.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category containing the section.
- `section_id` - ID of the section to update.
- `name` - New display name.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.contents.update_section(
    "01965f7a-0000-7000-8000-000000000005",
    "week-1",
    "01965f7a-0000-7000-8000-000000000011",
    name="Day 1 (Updated)",
)
```
<a id="srg.resources.contents.ContentsResource.delete_section"></a>

#### delete\_section

```python
def delete_section(content_id: str, category_name: str, section_id: str) -> None
```

Delete a section from a content item's category.

Permanently removes the section. Content items within the section
remain in the category but are no longer grouped.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category containing the section.
- `section_id` - ID of the section to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.contents.delete_section(
    "01965f7a-0000-7000-8000-000000000005",
    "week-1",
    "01965f7a-0000-7000-8000-000000000011",
)
```
<a id="srg.resources.contents.ContentsResource.patch_content_progression"></a>

#### patch\_content\_progression

```python
def patch_content_progression(
    content_id: str,
    *,
    status: ProgressionStatus
) -> ContentProgression
```

Update the current user's progression status for a content item.

Records whether the current API key user has started, is in progress
on, or has completed the specified content item. Progression data is
used for tracking learner completion within a hub profile.

**Arguments**:

- `content_id` - ID of the content item.
- `status` - New progression status — ``"NotStarted"``,
  ``"Incomplete"``, or ``"Completed"``.
  

**Returns**:

  ContentProgression reflecting the updated status.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.patch_media_progression"></a>

#### patch\_media\_progression

```python
def patch_media_progression(media_id: str, *, last_watched_time: int) -> None
```

Update the current user's last watched position in a media asset.

Records the playback position so the user can resume from where they
left off. Call this periodically during playback (e.g. every 30
seconds) and on pause / close.

**Arguments**:

- `media_id` - ID of the media asset.
- `last_watched_time` - Playback position in seconds.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.contents.patch_media_progression(
    "01965f7a-0000-7000-8000-000000000006",
    last_watched_time=95,
)
```
<a id="srg.resources.contents.ContentsResource.get_progression_stats"></a>

#### get\_progression\_stats

```python
def get_progression_stats(
    *,
    collection_id: str | None = None
) -> CollectionProgressionStats
```

Get progression statistics for the current user.

Returns the total number of content items and how many the current
user has completed. Optionally scoped to a single collection.

**Arguments**:

- `collection_id` - If provided, scopes the stats to the content
  items within that collection.
  

**Returns**:

  CollectionProgressionStats with ``total`` and ``completed``
  counts.
  

**Example**:

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
<a id="srg.resources.contents.ContentsResource.get_v2"></a>

#### get\_v2

```python
def get_v2(content_id: str) -> ContentV2
```

Get a content item by ID (v2).

Retrieves the content item using the v2 schema, which additionally
includes the main playable asset (with its HLS stream URL and
embed details), the current user's progression, and extended
metadata.

**Arguments**:

- `content_id` - ID of the content item to retrieve.
  

**Returns**:

  ContentV2 with extended metadata, main asset, and progression.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource"></a>

## AsyncContentsResource Objects

```python
class AsyncContentsResource()
```

<a id="srg.resources.contents.AsyncContentsResource.create"></a>

#### create

```python
async def create(
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
    categories: list[Any] | None = None
) -> Content | ContentUploadSignedUrl
```

Create a new content item in a hub profile.

Creates a content item or collection inside the given hub profile.

**Auto-upload mode** — pass ``cover_image`` as a local file path or an
``http(s)://`` URL. The SDK uploads the image and returns the fully
populated :class:`~srg.schemas.content.Content`.

**Manual mode** — pass ``cover`` as
:class:`~srg.schemas.common.ContentFileUploadParameters`. The API
returns :class:`~srg.schemas.content.ContentUploadSignedUrl` with a
signed URL so you can upload the image yourself.

**Arguments**:

- `name` - Display title of the content item.
- `hub_profile_id` - ID of the hub profile to create the content in.
- `privacy` - Visibility — ``"Preview"`` (default), ``"Private"``,
  or ``"Public"``.
- `details` - Optional body text / description.
- `url` - Optional external URL.
- `main_asset_id` - ID of the primary playable asset.
- `cover_image` - Local path or ``http(s)://`` URL of the cover image.
  Triggers auto-upload.
- `cover` - Cover image upload parameters (manual mode).
- `channels` - Channel and category placements.
- `context` - Additional context objects.
- `categories` - Category assignments.
  

**Returns**:

  :class:`~srg.schemas.content.Content` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.get"></a>

#### get

```python
async def get(content_id: str, *, hub_profile_id: str | None = None) -> Content
```

Get a content item by ID (v1).

**Arguments**:

- `content_id` - ID of the content item to retrieve.
- `hub_profile_id` - If provided, used to resolve access context.
  

**Returns**:

  Content object with metadata and channel placement details.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.update"></a>

#### update

```python
async def update(
    content_id: str,
    *,
    name: str,
    hub_profile_id: str | None = None,
    privacy: ContentPrivacy = "Preview",
    details: str | None = None,
    url: str | None = None,
    main_asset_id: str | None = None,
    cover_image: str | Path | None = None,
    cover: ContentFileUploadParameters | None = None,
    channels: list[str | ContentChannelUpsert] | None = None,
    context: list[Any] | None = None,
    categories: list[Any] | None = None
) -> Content | ContentUploadSignedUrl
```

Update a content item's metadata.

Replaces all metadata fields. **Auto-upload mode** — pass
``cover_image`` as a local file path or an ``http(s)://`` URL. The SDK
uploads the image and returns the updated
:class:`~srg.schemas.content.Content`. **Manual mode** — pass
``cover`` to get back
:class:`~srg.schemas.content.ContentUploadSignedUrl`.

**Arguments**:

- `content_id` - ID of the content item.
- `name` - New display title.
- `privacy` - New visibility level.
- `details` - New body text. Pass ``None`` to clear.
- `url` - New external URL. Pass ``None`` to clear.
- `main_asset_id` - New primary asset ID.
- `cover_image` - Local path or ``http(s)://`` URL of the new cover
  image. Triggers auto-upload.
- `cover` - Cover upload parameters (manual mode).
- `channels` - New channel/category placements.
- `context` - New context objects.
- `categories` - New category assignments.
  

**Returns**:

  :class:`~srg.schemas.content.Content` when ``cover_image`` is
  provided (auto-upload mode).
  :class:`~srg.schemas.content.ContentUploadSignedUrl` otherwise
  (manual mode).
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    content = await client.contents.update(
        "01965f7a-0000-7000-8000-000000000005",
        name="Welcome to the Team (v2)",
        privacy="Public",
        cover_image="/path/to/new_cover.jpg",
    )
```
  
  Example response:
```python
Content(
    id="01965f7a-0000-7000-8000-000000000005",
    name="Welcome to the Team (v2)",
    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
    cover=ContentCover(
        urls=CoverUrls(
            original="https://cdn.srgplus.com/covers/welcome-v2.jpg",
        ),
        extension="jpg",
        modified="2025-06-01T12:00:00Z",
    ),
    channels=[],
)
```
<a id="srg.resources.contents.AsyncContentsResource.filter"></a>

#### filter

```python
async def filter(
    hub_profile_id: str,
    *,
    page_size: int,
    cursor: str | None = None,
    only_archived: bool = False,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_contents: list[str] | None = None,
    types: list[str] | None = None
) -> CursorPagedList[ContentSearch]
```

List content items for a hub profile with cursor-based pagination.

**Arguments**:

- `hub_profile_id` - ID of the hub profile.
- `page_size` - Maximum number of items per page.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
- `only_archived` - If True, return only archived content.
- `exclude_categories` - Category IDs to exclude.
- `exclude_collections` - Collection IDs to exclude.
- `exclude_contents` - Content IDs to exclude.
- `types` - Content types to include (defaults to both ``"Content"``
  and ``"Collection"``).
  

**Returns**:

  CursorPagedList[ContentSearch] with content summaries and an
  optional cursor for the next page.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.search"></a>

#### search

```python
async def search(
    hub_profile_id: str,
    *,
    search: str,
    only_archived: bool = False,
    types: list[str] | None = None,
    exclude_categories: list[str] | None = None,
    exclude_collections: list[str] | None = None,
    exclude_contents: list[str] | None = None
) -> list[ContentSearch]
```

Search content items in a hub profile by name or keyword.

**Arguments**:

- `hub_profile_id` - ID of the hub profile.
- `search` - Search query string.
- `only_archived` - If True, search only archived content.
- `types` - Content types to include.
- `exclude_categories` - Category IDs to exclude.
- `exclude_collections` - Collection IDs to exclude.
- `exclude_contents` - Content IDs to exclude.
  

**Returns**:

  List of ContentSearch objects matching the query.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.add_to_categories"></a>

#### add\_to\_categories

```python
async def add_to_categories(content_id: str, body: dict) -> None
```

Add a content item to one or more channel categories.

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body specifying which channel categories to add
  the content to.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.remove_from_categories"></a>

#### remove\_from\_categories

```python
async def remove_from_categories(content_id: str, body: dict) -> None
```

Remove a content item from one or more channel categories.

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body specifying which channel categories to remove
  the content from.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.move"></a>

#### move

```python
async def move(content_id: str, body: dict) -> None
```

Move a content item to a different channel category.

**Arguments**:

- `content_id` - ID of the content item.
- `body` - Request body with source and destination category positions.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.create_section"></a>

#### create\_section

```python
async def create_section(
    content_id: str,
    category_name: str,
    *,
    name: str
) -> None
```

Create a section in a content item's category.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category.
- `name` - Display name of the new section.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.contents.create_section(
        "01965f7a-0000-7000-8000-000000000005",
        "week-1",
        name="Day 1",
    )
```
<a id="srg.resources.contents.AsyncContentsResource.update_section"></a>

#### update\_section

```python
async def update_section(
    content_id: str,
    category_name: str,
    section_id: str,
    *,
    name: str
) -> None
```

Update the name of a section in a content item's category.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category.
- `section_id` - ID of the section to update.
- `name` - New display name.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.contents.update_section(
        "01965f7a-0000-7000-8000-000000000005",
        "week-1",
        "01965f7a-0000-7000-8000-000000000011",
        name="Day 1 (Updated)",
    )
```
<a id="srg.resources.contents.AsyncContentsResource.delete_section"></a>

#### delete\_section

```python
async def delete_section(
    content_id: str,
    category_name: str,
    section_id: str
) -> None
```

Delete a section from a content item's category.

**Arguments**:

- `content_id` - ID of the collection content item.
- `category_name` - Name slug of the category.
- `section_id` - ID of the section to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.contents.delete_section(
        "01965f7a-0000-7000-8000-000000000005",
        "week-1",
        "01965f7a-0000-7000-8000-000000000011",
    )
```
<a id="srg.resources.contents.AsyncContentsResource.patch_content_progression"></a>

#### patch\_content\_progression

```python
async def patch_content_progression(
    content_id: str,
    *,
    status: ProgressionStatus
) -> ContentProgression
```

Update the current user's progression status for a content item.

**Arguments**:

- `content_id` - ID of the content item.
- `status` - New status — ``"NotStarted"``, ``"Incomplete"``, or
  ``"Completed"``.
  

**Returns**:

  ContentProgression reflecting the updated status.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.patch_media_progression"></a>

#### patch\_media\_progression

```python
async def patch_media_progression(
    media_id: str,
    *,
    last_watched_time: int
) -> None
```

Update the current user's last watched position in a media asset.

**Arguments**:

- `media_id` - ID of the media asset.
- `last_watched_time` - Playback position in seconds.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.contents.patch_media_progression(
        "01965f7a-0000-7000-8000-000000000006",
        last_watched_time=95,
    )
```
<a id="srg.resources.contents.AsyncContentsResource.get_progression_stats"></a>

#### get\_progression\_stats

```python
async def get_progression_stats(
    *,
    collection_id: str | None = None
) -> CollectionProgressionStats
```

Get progression statistics for the current user.

**Arguments**:

- `collection_id` - If provided, scopes the stats to the content
  items within that collection.
  

**Returns**:

  CollectionProgressionStats with ``total`` and ``completed``
  counts.
  

**Example**:

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
<a id="srg.resources.contents.AsyncContentsResource.get_v2"></a>

#### get\_v2

```python
async def get_v2(content_id: str) -> ContentV2
```

Get a content item by ID (v2).

Retrieves the content item using the v2 schema, which additionally
includes the main playable asset, the current user's progression,
and extended metadata.

**Arguments**:

- `content_id` - ID of the content item to retrieve.
  

**Returns**:

  ContentV2 with extended metadata, main asset, and progression.
  

**Example**:

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