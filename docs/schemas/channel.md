## Category

*model* `Category(id, name, is_archived=False, is_pinned=False, notifications_enabled=True, sections=[], options=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **is_archived** (*bool, optional*) – Defaults to `False`.
- **is_pinned** (*bool, optional*) – Defaults to `False`.
- **notifications_enabled** (*bool, optional*) – Defaults to `True`.
- **sections** (*list[Section], optional*) – Defaults to `[]`.
- **options** (*ChannelCategoryOptions | None, optional*) – Defaults to `None`.

## CategoryHeadingContent

*model* `CategoryHeadingContent(references=[], total_count=0, next_cursor=None, has_next=False)`

Paginated heading content inside a v2 category.

**Fields**

- **references** (*list[Any], optional*) – Defaults to `[]`.
- **total_count** (*int, optional*) – Defaults to `0`.
- **next_cursor** (*str | None, optional*) – Defaults to `None`.
- **has_next** (*bool, optional*) – Defaults to `False`.

## CategoryToReorder

*model* `CategoryToReorder(id, order=None)`

**Fields**

- **id** (*str*)
- **order** (*int | None, optional*) – Defaults to `None`.

## CategoryWithHeadingContent

*model* `CategoryWithHeadingContent(id, name, is_archived=False, is_pinned=False, notifications_enabled=False, sections=[], options=None, heading_content=None)`

Category shape returned inside HubProfileChannelV2Response.

**Fields**

- **id** (*str*)
- **name** (*str*)
- **is_archived** (*bool, optional*) – Defaults to `False`.
- **is_pinned** (*bool, optional*) – Defaults to `False`.
- **notifications_enabled** (*bool, optional*) – Defaults to `False`.
- **sections** (*list[Section], optional*) – Defaults to `[]`.
- **options** (*ChannelCategoryOptionsV2 | None, optional*) – Defaults to `None`.
- **heading_content** (*CategoryHeadingContent | None, optional*) – Defaults to `None`.

## CategoryWithHubProfile

*model* `CategoryWithHubProfile(id, name, is_archived=False, is_pinned=False, notifications_enabled=False, heading_content=None, hub_profile_id, hub_profile_name=None, hub_profile_user_name=None)`

GET /api/v2/channels/\{hubProfileUserName\}/\{channelName\}/categories/\{name\}

**Fields**

- **id** (*str*)
- **name** (*str*)
- **is_archived** (*bool, optional*) – Defaults to `False`.
- **is_pinned** (*bool, optional*) – Defaults to `False`.
- **notifications_enabled** (*bool, optional*) – Defaults to `False`.
- **heading_content** (*CategoryHeadingContent | None, optional*) – Defaults to `None`.
- **hub_profile_id** (*str*)
- **hub_profile_name** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_user_name** (*str | None, optional*) – Defaults to `None`.

## Channel

*model* `Channel(id, name, categories=[])`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **categories** (*list[Category], optional*) – Defaults to `[]`.

## ChannelCategoryOptions

*model* `ChannelCategoryOptions(view=None, progression=None, cover=None, expandable=True)`

**Fields**

- **view** (*dict | None, optional*) – Defaults to `None`.
- **progression** (*dict | None, optional*) – Defaults to `None`.
- **cover** (*dict | None, optional*) – Defaults to `None`.
- **expandable** (*bool, optional*) – Defaults to `True`.

## ChannelCategoryOptionsUpsert

*model* `ChannelCategoryOptionsUpsert(view=ViewOptionsUpsert(type=None), progression=ProgressionOptionsUpsert(enabled=False), cover=CoverOptionsUpsert(show=True), expandable=True)`

**Fields**

- **view** (*ViewOptionsUpsert, optional*) – Defaults to `ViewOptionsUpsert(type=None)`.
- **progression** (*ProgressionOptionsUpsert, optional*) – Defaults to `ProgressionOptionsUpsert(enabled=False)`.
- **cover** (*CoverOptionsUpsert, optional*) – Defaults to `CoverOptionsUpsert(show=True)`.
- **expandable** (*bool, optional*) – Defaults to `True`.

## ChannelCategoryOptionsV2

*model* `ChannelCategoryOptionsV2(expandable=True, view=None, cover=None, progression=None)`

**Fields**

- **expandable** (*bool, optional*) – Defaults to `True`.
- **view** (*ViewOptions | None, optional*) – Defaults to `None`.
- **cover** (*CoverOptions | None, optional*) – Defaults to `None`.
- **progression** (*ProgressionOptions | None, optional*) – Defaults to `None`.

## CoverOptions

*model* `CoverOptions(aspect=None)`

**Fields**

- **aspect** (*Any | None, optional*) – Defaults to `None`.

## CoverOptionsUpsert

*model* `CoverOptionsUpsert(show=True)`

**Fields**

- **show** (*bool, optional*) – Defaults to `True`.

## HubProfileChannel

*model* `HubProfileChannel(id, name, privacy=None, hub_profile_id=None, hub_profile_name=None, hub_profile_user_name=None, is_archived=False, can_edit=False, can_archive=False, can_manage=False, categories=[])`

Channel response returned by GET /api/v1/channels (list endpoint).

**Fields**

- **id** (*str*)
- **name** (*str*)
- **privacy** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_id** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_name** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_user_name** (*str | None, optional*) – Defaults to `None`.
- **is_archived** (*bool, optional*) – Defaults to `False`.
- **can_edit** (*bool, optional*) – Defaults to `False`.
- **can_archive** (*bool, optional*) – Defaults to `False`.
- **can_manage** (*bool, optional*) – Defaults to `False`.
- **categories** (*list[Category], optional*) – Defaults to `[]`.

## HubProfileChannelV2

*model* `HubProfileChannelV2(id, name, privacy=None, hub_profile_name=None, hub_profile_user_name=None, categories=[])`

GET /api/v2/channels/\{channelId\} or /\{hubProfileUserName\}/\{channelName\}

**Fields**

- **id** (*str*)
- **name** (*str*)
- **privacy** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_name** (*str | None, optional*) – Defaults to `None`.
- **hub_profile_user_name** (*str | None, optional*) – Defaults to `None`.
- **categories** (*list[CategoryWithHeadingContent], optional*) – Defaults to `[]`.

## OrderedContentToCategoryReference

*model* `OrderedContentToCategoryReference(content_id, section_id=None, order=None)`

**Fields**

- **content_id** (*str*)
- **section_id** (*str | None, optional*) – Defaults to `None`.
- **order** (*int | None, optional*) – Defaults to `None`.

## ProgressionOptions

*model* `ProgressionOptions(progression=False, sequential_completion=False)`

**Fields**

- **progression** (*bool, optional*) – Defaults to `False`.
- **sequential_completion** (*bool, optional*) – Defaults to `False`.

## ProgressionOptionsUpsert

*model* `ProgressionOptionsUpsert(enabled=False)`

**Fields**

- **enabled** (*bool, optional*) – Defaults to `False`.

## Section

*model* `Section(id, name=None, cursor=None, is_empty=False, type=None)`

**Fields**

- **id** (*str*)
- **name** (*str | None, optional*) – Defaults to `None`.
- **cursor** (*str | None, optional*) – Defaults to `None`.
- **is_empty** (*bool, optional*) – Defaults to `False`.
- **type** (*str | None, optional*) – Defaults to `None`.

## SectionBaseCreate

*model* `SectionBaseCreate(dollar_type, name, reference_ids=[])`

**Fields**

- **dollar_type** (*str*)
- **name** (*str*)
- **reference_ids** (*list[str], optional*) – Defaults to `[]`.

## ViewOptions

*model* `ViewOptions(presentation=None)`

**Fields**

- **presentation** (*Any | None, optional*) – Defaults to `None`.

## ViewOptionsUpsert

*model* `ViewOptionsUpsert(type=None)`

**Fields**

- **type** (*str | None, optional*) – Defaults to `None`.
