## CollectionProgression

*model* `CollectionProgression(status=None, total=0, completed=0)`

**Fields**

- **status** (*str | None, optional*) – Defaults to `None`.
- **total** (*int, optional*) – Defaults to `0`.
- **completed** (*int, optional*) – Defaults to `0`.

## CollectionProgressionStats

*model* `CollectionProgressionStats(total=0, completed=0)`

**Fields**

- **total** (*int, optional*) – Defaults to `0`.
- **completed** (*int, optional*) – Defaults to `0`.

## Content

*model* `Content(id, name, details, url, created_by, hub_profile_id, hub_profile_name, created, archived, cover, channels=[], heading_referenced_content=[])`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **details** (*str | None*)
- **url** (*str | None*)
- **created_by** (*str*)
- **hub_profile_id** (*str*)
- **hub_profile_name** (*str | None*)
- **created** (*datetime*)
- **archived** (*datetime | None*)
- **cover** (*ContentCover | None*)
- **channels** (*list[ContentChannel], optional*) – Defaults to `[]`.
- **heading_referenced_content** (*list[OrderedContentCategoryReference], optional*) – Defaults to `[]`.

## ContentChannel

*model* `ContentChannel(id, name, categories=[])`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **categories** (*list[ContentChannelCategory], optional*) – Defaults to `[]`.

## ContentChannelCategory

*model* `ContentChannelCategory(id, name)`

**Fields**

- **id** (*str*)
- **name** (*str*)

## ContentChannelUpsert

*model* `ContentChannelUpsert(channel_id, category_ids=[])`

**Fields**

- **channel_id** (*str*)
- **category_ids** (*list[str], optional*) – Defaults to `[]`.

## ContentProgression

*model* `ContentProgression(status=None)`

**Fields**

- **status** (*str | None, optional*) – Defaults to `None`.

## ContentSearch

*model* `ContentSearch(id, name, hub_profile_id=None, cover=None, privacy=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **hub_profile_id** (*str | None, optional*) – Defaults to `None`.
- **cover** (*ContentCover | None, optional*) – Defaults to `None`.
- **privacy** (*str | None, optional*) – Defaults to `None`.

## ContentUploadSignedUrl

*model* `ContentUploadSignedUrl(id, cover_signed_url=None, cover_extension=None, context=[], metadata_headers=None)`

**Fields**

- **id** (*str*)
- **cover_signed_url** (*SignedUrl | None, optional*) – Defaults to `None`.
- **cover_extension** (*str | None, optional*) – Defaults to `None`.
- **context** (*list[Any], optional*) – Defaults to `[]`.
- **metadata_headers** (*dict[str, str] | None, optional*) – Defaults to `None`.

## ContentV2

*model* `ContentV2(id, privacy, name, details=None, url=None, created_by, hub_profile_id, hub_profile_name=None, main_asset=None, context=[], created, archived=None, cover=None, channels=[], categories=[], progression=None)`

GET /api/v2/contents/\{contentId\}

**Fields**

- **id** (*str*)
- **privacy** (*str*)
- **name** (*str*)
- **details** (*str | None, optional*) – Defaults to `None`.
- **url** (*str | None, optional*) – Defaults to `None`.
- **created_by** (*str*)
- **hub_profile_id** (*str*)
- **hub_profile_name** (*str | None, optional*) – Defaults to `None`.
- **main_asset** (*MainPlayableAsset | None, optional*) – Defaults to `None`.
- **context** (*list[Any], optional*) – Defaults to `[]`.
- **created** (*datetime*)
- **archived** (*datetime | None, optional*) – Defaults to `None`.
- **cover** (*ContentCover | None, optional*) – Defaults to `None`.
- **channels** (*list[ContentChannel], optional*) – Defaults to `[]`.
- **categories** (*list[Any], optional*) – Defaults to `[]`.
- **progression** (*ContentProgression | None, optional*) – Defaults to `None`.

## ContentWidgetCreate

*model* `ContentWidgetCreate(dollar_type='ContentWidget', title=None, content_id)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'ContentWidget'`.
- **title** (*str | None, optional*) – Defaults to `None`.
- **content_id** (*str*)

## CustomLinkCreate

*model* `CustomLinkCreate(dollar_type='CustomLink', label, url)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'CustomLink'`.
- **label** (*str*)
- **url** (*str*)

## HubProfileWidgetCreate

*model* `HubProfileWidgetCreate(dollar_type='HubProfile', title=None, hub_profile_id)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'HubProfile'`.
- **title** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_id** (*str*)

## KnownLinkCreate

*model* `KnownLinkCreate(dollar_type='KnownLink', type, url)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'KnownLink'`.
- **type** (*str*)
- **url** (*str*)

## LinkListCreate

*model* `LinkListCreate(dollar_type='LinkList', title=None, links=[])`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'LinkList'`.
- **title** (*str | None, optional*) – Defaults to `None`.
- **links** (*list[Any], optional*) – Defaults to `[]`.

## MainPlayableAsset

*model* `MainPlayableAsset(id, name, cover=None, duration_in_seconds=None, url=None, iframe_url=None, external_media_id=None, hls_stream_url=None, original_stream_url=None, status=None, progression=None)`

Polymorphic main asset ($type: Embed | Media | Video).

    All derived fields are optional so a single model handles all variants.

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*ContentCover | None, optional*) – Defaults to `None`.
- **duration_in_seconds** (*int | None, optional*) – Defaults to `None`.
- **url** (*str | None, optional*) – Defaults to `None`.
- **iframe_url** (*str | None, optional*) – Defaults to `None`.
- **external_media_id** (*str | None, optional*) – Defaults to `None`.
- **hls_stream_url** (*str | None, optional*) – Defaults to `None`.
- **original_stream_url** (*str | None, optional*) – Defaults to `None`.
- **status** (*str | None, optional*) – Defaults to `None`.
- **progression** (*MediaProgression | None, optional*) – Defaults to `None`.

## MediaProgression

*model* `MediaProgression(last_watched_time=None, status=None)`

**Fields**

- **last_watched_time** (*int | None, optional*) – Defaults to `None`.
- **status** (*str | None, optional*) – Defaults to `None`.

## MediaWidgetCreate

*model* `MediaWidgetCreate(dollar_type='Media', title=None, asset_id, autoplay=False)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Media'`.
- **title** (*str | None, optional*) – Defaults to `None`.
- **asset_id** (*str*)
- **autoplay** (*bool, optional*) – Defaults to `False`.

## OrderedContentCategoryReference

*model* `OrderedContentCategoryReference(channel_id=None, category_id=None, order=None)`

**Fields**

- **channel_id** (*str | None, optional*) – Defaults to `None`.
- **category_id** (*str | None, optional*) – Defaults to `None`.
- **order** (*int | None, optional*) – Defaults to `None`.

## TextWidgetCreate

*model* `TextWidgetCreate(dollar_type='Text', title=None, content)`

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Text'`.
- **title** (*str | None, optional*) – Defaults to `None`.
- **content** (*str*)
