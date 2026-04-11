<a id="srg.resources.channels"></a>

# srg.resources.channels

<a id="srg.resources.channels.ChannelsResource"></a>

## ChannelsResource Objects

```python
class ChannelsResource()
```

<a id="srg.resources.channels.ChannelsResource.create"></a>

#### create

```python
def create(
    *,
    name: str,
    hub_profile_id: str,
    privacy: ChannelPrivacy = "Private"
) -> str
```

Create a new channel in a hub profile.

Channels are the primary organizational unit inside a hub profile.
They contain categories, which in turn contain sections and content.

**Arguments**:

- `name` - Display name of the new channel.
- `hub_profile_id` - ID of the hub profile to create the channel in.
- `privacy` - Channel visibility — ``"Private"`` (default, only
  members can see it) or ``"Public"`` (visible to anyone).
  

**Returns**:

  ID of the newly created channel.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channel_id = client.channels.create(
    name="Onboarding",
    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
    privacy="Public",
)
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000003"
```
<a id="srg.resources.channels.ChannelsResource.list"></a>

#### list

```python
def list(
    hub_profile_id: str,
    *,
    include_archived: bool = False
) -> list[Channel]
```

List all channels for a hub profile.

Returns every channel in the hub profile, along with their
categories. Archived channels are excluded by default.

**Arguments**:

- `hub_profile_id` - ID of the hub profile.
- `include_archived` - If True, include archived channels in the
  result. Defaults to False.
  

**Returns**:

  List of Channel objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channels = client.channels.list("01965f7a-0000-7000-8000-000000000002")
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
<a id="srg.resources.channels.ChannelsResource.get"></a>

#### get

```python
def get(channel_id: str) -> HubProfileChannelV2
```

Get detailed channel data by ID (v2).

Retrieves the full channel details using the v2 schema, which includes
categories with their heading content (a preview of pinned content
items at the top of each category).

**Arguments**:

- `channel_id` - ID of the channel to retrieve.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channel = client.channels.get("01965f7a-0000-7000-8000-000000000003")
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
<a id="srg.resources.channels.ChannelsResource.get_by_name"></a>

#### get\_by\_name

```python
def get_by_name(
    hub_profile_username: str,
    channel_name: str
) -> HubProfileChannelV2
```

Get detailed channel data by hub profile username and channel name (v2).

Retrieves a channel using human-readable slugs instead of IDs. Useful
for public-facing integrations where you only know the profile and
channel names.

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile (e.g.
  ``"acme-academy"``).
- `channel_name` - Name slug of the channel (e.g. ``"onboarding"``).
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channel = client.channels.get_by_name("acme-academy", "onboarding")
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
<a id="srg.resources.channels.ChannelsResource.update"></a>

#### update

```python
def update(
    *,
    channel_id: str,
    hub_profile_id: str,
    name: str,
    privacy: ChannelPrivacy | None = None,
    categories: builtins.list[CategoryToReorder] | None = None
) -> None
```

Update a channel's name, privacy, and category order.

Replaces the channel's name and optionally updates its privacy
setting and category ordering. All provided fields are overwritten.

**Arguments**:

- `channel_id` - ID of the channel to update.
- `hub_profile_id` - ID of the hub profile the channel belongs to.
- `name` - New display name for the channel.
- `privacy` - New privacy setting. Unchanged if not provided.
- `categories` - New category ordering. Each entry specifies a category
  ID and its new ``order`` index. Unchanged if not provided.
  

**Example**:

```python
from sdk.schemas.channel import CategoryToReorder

client = SRGClient(api_key="srgplus_your_key")
client.channels.update(
    channel_id="01965f7a-0000-7000-8000-000000000003",
    hub_profile_id="01965f7a-0000-7000-8000-000000000002",
    name="Onboarding (Updated)",
    privacy="Public",
    categories=[
        CategoryToReorder(id="01965f7a-0000-7000-8000-000000000004", order=0),
    ],
)
```
<a id="srg.resources.channels.ChannelsResource.archive"></a>

#### archive

```python
def archive(channel_id: str) -> None
```

Archive a channel.

Moves the channel to an archived state. Its content is preserved
but the channel is hidden from members.

**Arguments**:

- `channel_id` - ID of the channel to archive.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.archive("01965f7a-0000-7000-8000-000000000003")
```
<a id="srg.resources.channels.ChannelsResource.delete"></a>

#### delete

```python
def delete(channel_id: str) -> None
```

Permanently delete a channel.

Removes the channel and all of its categories, sections, and content
references. This action is irreversible.

**Arguments**:

- `channel_id` - ID of the channel to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.delete("01965f7a-0000-7000-8000-000000000003")
```
<a id="srg.resources.channels.ChannelsResource.create_category"></a>

#### create\_category

```python
def create_category(
    channel_id: str,
    *,
    name: str,
    is_pinned: bool = False,
    notifications_enabled: bool = True,
    options: ChannelCategoryOptionsUpsert | None = None,
    sections: builtins.list[SectionBaseCreate] | None = None
) -> str
```

Create a new category inside a channel.

Categories group content within a channel. Optionally, initial
sections and display options can be provided at creation time.

**Arguments**:

- `channel_id` - ID of the channel to add the category to.
- `name` - Display name of the new category.
- `is_pinned` - Whether to pin the category to the top of the
  channel. Defaults to False.
- `notifications_enabled` - Whether to send notifications for new
  content in this category. Defaults to True.
- `options` - Display and behaviour options (view type, progression
  tracking, cover visibility, expandable). If omitted, defaults
  are used.
- `sections` - Initial sections to create inside the category.
  

**Returns**:

  ID of the newly created category.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
category_id = client.channels.create_category(
    "01965f7a-0000-7000-8000-000000000003",
    name="Week 1",
    is_pinned=True,
)
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000004"
```
<a id="srg.resources.channels.ChannelsResource.update_category"></a>

#### update\_category

```python
def update_category(
    channel_id: str,
    category_id: str,
    *,
    name: str,
    is_pinned: bool = False,
    notifications_enabled: bool = True,
    options: ChannelCategoryOptionsUpsert | None = None
) -> None
```

Update a category's name, pin status, notifications, and display options.

Replaces all category settings with the provided values. All fields
are overwritten.

**Arguments**:

- `channel_id` - ID of the channel the category belongs to.
- `category_id` - ID of the category to update.
- `name` - New display name.
- `is_pinned` - Whether to pin the category. Defaults to False.
- `notifications_enabled` - Whether notifications are enabled. Defaults
  to True.
- `options` - Updated display and behaviour options.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.update_category(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    name="Week 1 (Updated)",
    is_pinned=False,
)
```
<a id="srg.resources.channels.ChannelsResource.archive_category"></a>

#### archive\_category

```python
def archive_category(channel_id: str, category_id: str) -> None
```

Archive a category.

Moves the category to an archived state. Content references within
the category are preserved but it is hidden from members.

**Arguments**:

- `channel_id` - ID of the channel the category belongs to.
- `category_id` - ID of the category to archive.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.archive_category(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
)
```
<a id="srg.resources.channels.ChannelsResource.delete_category"></a>

#### delete\_category

```python
def delete_category(channel_id: str, category_id: str) -> None
```

Permanently delete a category from a channel.

Removes the category and all of its sections and content references.
This action is irreversible.

**Arguments**:

- `channel_id` - ID of the channel the category belongs to.
- `category_id` - ID of the category to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.delete_category(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
)
```
<a id="srg.resources.channels.ChannelsResource.get_category_references"></a>

#### get\_category\_references

```python
def get_category_references(
    channel_id: str,
    category_id: str,
    *,
    page_size: int = 20,
    cursor: str | None = None
) -> CursorPagedList[OrderedContentToCategoryReference]
```

List content references in a category with cursor-based pagination.

Returns a page of ordered content-to-category reference objects,
each identifying a content item placed in this category and its
position within the category.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `page_size` - Maximum number of references to return per page.
  Defaults to 20.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
  

**Returns**:

  CursorPagedList[OrderedContentToCategoryReference] with content
  references and an optional cursor for the next page.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
page = client.channels.get_category_references(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    page_size=10,
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
<a id="srg.resources.channels.ChannelsResource.create_section"></a>

#### create\_section

```python
def create_section(
    channel_id: str,
    category_id: str,
    *,
    name: str
) -> str
```

Create a new section inside a channel category.

Sections subdivide a category into named groups of content. Content
items are placed into a section when added to a category.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category to add the section to.
- `name` - Display name of the new section.
  

**Returns**:

  ID of the newly created section.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
section_id = client.channels.create_section(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    name="Videos",
)
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000011"
```
<a id="srg.resources.channels.ChannelsResource.update_section"></a>

#### update\_section

```python
def update_section(
    channel_id: str,
    category_id: str,
    section_id: str,
    *,
    name: str
) -> None
```

Update the name of a section.

Renames the section. Does not affect the content items it contains.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category containing the section.
- `section_id` - ID of the section to update.
- `name` - New display name for the section.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.update_section(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    "01965f7a-0000-7000-8000-000000000011",
    name="Training Videos",
)
```
<a id="srg.resources.channels.ChannelsResource.delete_section"></a>

#### delete\_section

```python
def delete_section(channel_id: str, category_id: str, section_id: str) -> None
```

Permanently delete a section from a channel category.

Removes the section and all content references within it. This
action is irreversible.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category containing the section.
- `section_id` - ID of the section to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.delete_section(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    "01965f7a-0000-7000-8000-000000000011",
)
```
<a id="srg.resources.channels.ChannelsResource.add_content_to_category"></a>

#### add\_content\_to\_category

```python
def add_content_to_category(
    channel_id: str,
    category_id: str,
    section_id: str,
    *,
    contents_ids: builtins.list[str]
) -> None
```

Add content items to a category section.

Places one or more content items into the specified section of a
channel category. Duplicate additions are ignored.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `section_id` - ID of the section within the category.
- `contents_ids` - List of content IDs to add.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.channels.add_content_to_category(
    "01965f7a-0000-7000-8000-000000000003",
    "01965f7a-0000-7000-8000-000000000004",
    "01965f7a-0000-7000-8000-000000000011",
    contents_ids=[
        "01965f7a-0000-7000-8000-000000000005",
        "01965f7a-0000-7000-8000-000000000012",
    ],
)
```
<a id="srg.resources.channels.ChannelsResource.get_v2"></a>

#### get\_v2

```python
def get_v2(channel_id: str) -> HubProfileChannelV2
```

Get detailed channel data by ID (v2).

Alias for ``get``. Retrieves the full channel details using the v2
schema, including categories with heading content.

**Arguments**:

- `channel_id` - ID of the channel to retrieve.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channel = client.channels.get_v2("01965f7a-0000-7000-8000-000000000003")
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
<a id="srg.resources.channels.ChannelsResource.get_by_name_v2"></a>

#### get\_by\_name\_v2

```python
def get_by_name_v2(
    hub_profile_username: str,
    channel_name: str
) -> HubProfileChannelV2
```

Get detailed channel data by hub profile username and channel name (v2).

Alias for ``get_by_name``. Retrieves a channel using human-readable
slugs instead of IDs.

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile.
- `channel_name` - Name slug of the channel.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
channel = client.channels.get_by_name_v2("acme-academy", "onboarding")
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
<a id="srg.resources.channels.ChannelsResource.get_category_v2"></a>

#### get\_category\_v2

```python
def get_category_v2(
    hub_profile_username: str,
    channel_name: str,
    category_name: str
) -> CategoryWithHubProfile
```

Get category details by hub profile username, channel name, and category name (v2).

Retrieves a specific category using human-readable slugs for the hub
profile, channel, and category. The response includes the hub profile
context alongside the category data and its heading content.

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile.
- `channel_name` - Name slug of the channel.
- `category_name` - Name slug of the category.
  

**Returns**:

  CategoryWithHubProfile containing category details and the
  associated hub profile context.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
category = client.channels.get_category_v2(
    "acme-academy",
    "onboarding",
    "week-1",
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
<a id="srg.resources.channels.AsyncChannelsResource"></a>

## AsyncChannelsResource Objects

```python
class AsyncChannelsResource()
```

<a id="srg.resources.channels.AsyncChannelsResource.create"></a>

#### create

```python
async def create(
    *,
    name: str,
    hub_profile_id: str,
    privacy: str = "Private"
) -> str
```

Create a new channel in a hub profile.

Channels are the primary organizational unit inside a hub profile.
They contain categories, which in turn contain sections and content.

**Arguments**:

- `name` - Display name of the new channel.
- `hub_profile_id` - ID of the hub profile to create the channel in.
- `privacy` - Channel visibility — ``"Private"`` (default) or
  ``"Public"``.
  

**Returns**:

  ID of the newly created channel.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channel_id = await client.channels.create(
        name="Onboarding",
        hub_profile_id="01965f7a-0000-7000-8000-000000000002",
        privacy="Public",
    )
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000003"
```
<a id="srg.resources.channels.AsyncChannelsResource.list"></a>

#### list

```python
async def list(
    hub_profile_id: str,
    *,
    include_archived: bool = False
) -> list[Channel]
```

List all channels for a hub profile.

Returns every channel in the hub profile along with their categories.
Archived channels are excluded by default.

**Arguments**:

- `hub_profile_id` - ID of the hub profile.
- `include_archived` - If True, include archived channels. Defaults to
  False.
  

**Returns**:

  List of Channel objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channels = await client.channels.list(
        "01965f7a-0000-7000-8000-000000000002"
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
<a id="srg.resources.channels.AsyncChannelsResource.get"></a>

#### get

```python
async def get(channel_id: str) -> HubProfileChannelV2
```

Get detailed channel data by ID (v2).

Retrieves the full channel details using the v2 schema, which includes
categories with their heading content.

**Arguments**:

- `channel_id` - ID of the channel to retrieve.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channel = await client.channels.get(
        "01965f7a-0000-7000-8000-000000000003"
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
<a id="srg.resources.channels.AsyncChannelsResource.get_by_name"></a>

#### get\_by\_name

```python
async def get_by_name(
    hub_profile_username: str,
    channel_name: str
) -> HubProfileChannelV2
```

Get detailed channel data by hub profile username and channel name (v2).

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile.
- `channel_name` - Name slug of the channel.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channel = await client.channels.get_by_name("acme-academy", "onboarding")
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
<a id="srg.resources.channels.AsyncChannelsResource.update"></a>

#### update

```python
async def update(
    *,
    channel_id: str,
    hub_profile_id: str,
    name: str,
    privacy: ChannelPrivacy | None = None,
    categories: builtins.list[CategoryToReorder] | None = None
) -> None
```

Update a channel's name, privacy, and category order.

Replaces the channel's name and optionally its privacy setting and
category ordering.

**Arguments**:

- `channel_id` - ID of the channel to update.
- `hub_profile_id` - ID of the hub profile the channel belongs to.
- `name` - New display name for the channel.
- `privacy` - New privacy setting. Unchanged if not provided.
- `categories` - New category ordering. Unchanged if not provided.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.update(
        channel_id="01965f7a-0000-7000-8000-000000000003",
        hub_profile_id="01965f7a-0000-7000-8000-000000000002",
        name="Onboarding (Updated)",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.archive"></a>

#### archive

```python
async def archive(channel_id: str) -> None
```

Archive a channel.

Moves the channel to an archived state.

**Arguments**:

- `channel_id` - ID of the channel to archive.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.archive("01965f7a-0000-7000-8000-000000000003")
```
<a id="srg.resources.channels.AsyncChannelsResource.delete"></a>

#### delete

```python
async def delete(channel_id: str) -> None
```

Permanently delete a channel.

Removes the channel and all of its categories, sections, and content
references. This action is irreversible.

**Arguments**:

- `channel_id` - ID of the channel to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.delete("01965f7a-0000-7000-8000-000000000003")
```
<a id="srg.resources.channels.AsyncChannelsResource.create_category"></a>

#### create\_category

```python
async def create_category(
    channel_id: str,
    *,
    name: str,
    is_pinned: bool = False,
    notifications_enabled: bool = True,
    options: ChannelCategoryOptionsUpsert | None = None,
    sections: builtins.list[SectionBaseCreate] | None = None
) -> str
```

Create a new category inside a channel.

**Arguments**:

- `channel_id` - ID of the channel to add the category to.
- `name` - Display name of the new category.
- `is_pinned` - Whether to pin the category. Defaults to False.
- `notifications_enabled` - Whether to send notifications for new
  content. Defaults to True.
- `options` - Display and behaviour options.
- `sections` - Initial sections to create inside the category.
  

**Returns**:

  ID of the newly created category.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    category_id = await client.channels.create_category(
        "01965f7a-0000-7000-8000-000000000003",
        name="Week 1",
        is_pinned=True,
    )
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000004"
```
<a id="srg.resources.channels.AsyncChannelsResource.update_category"></a>

#### update\_category

```python
async def update_category(
    channel_id: str,
    category_id: str,
    *,
    name: str,
    is_pinned: bool = False,
    notifications_enabled: bool = True,
    options: ChannelCategoryOptionsUpsert | None = None
) -> None
```

Update a category's name, pin status, notifications, and display options.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category to update.
- `name` - New display name.
- `is_pinned` - Whether to pin the category. Defaults to False.
- `notifications_enabled` - Whether notifications are enabled.
  Defaults to True.
- `options` - Updated display and behaviour options.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.update_category(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
        name="Week 1 (Updated)",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.archive_category"></a>

#### archive\_category

```python
async def archive_category(channel_id: str, category_id: str) -> None
```

Archive a category.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category to archive.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.archive_category(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.delete_category"></a>

#### delete\_category

```python
async def delete_category(channel_id: str, category_id: str) -> None
```

Permanently delete a category from a channel.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.delete_category(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.get_category_references"></a>

#### get\_category\_references

```python
async def get_category_references(
    channel_id: str,
    category_id: str,
    *,
    page_size: int = 20,
    cursor: str | None = None
) -> CursorPagedList[OrderedContentToCategoryReference]
```

List content references in a category with cursor-based pagination.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `page_size` - Maximum number of references per page. Defaults to 20.
- `cursor` - Opaque cursor from the previous response. Omit for the
  first page.
  

**Returns**:

  CursorPagedList[OrderedContentToCategoryReference].
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    page = await client.channels.get_category_references(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
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
<a id="srg.resources.channels.AsyncChannelsResource.create_section"></a>

#### create\_section

```python
async def create_section(
    channel_id: str,
    category_id: str,
    *,
    name: str
) -> str
```

Create a new section inside a channel category.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `name` - Display name of the new section.
  

**Returns**:

  ID of the newly created section.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    section_id = await client.channels.create_section(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
        name="Videos",
    )
```
  
  Example response:
```python
"01965f7a-0000-7000-8000-000000000011"
```
<a id="srg.resources.channels.AsyncChannelsResource.update_section"></a>

#### update\_section

```python
async def update_section(
    channel_id: str,
    category_id: str,
    section_id: str,
    *,
    name: str
) -> None
```

Update the name of a section.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `section_id` - ID of the section to update.
- `name` - New display name.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.update_section(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
        "01965f7a-0000-7000-8000-000000000011",
        name="Training Videos",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.delete_section"></a>

#### delete\_section

```python
async def delete_section(
    channel_id: str,
    category_id: str,
    section_id: str
) -> None
```

Permanently delete a section from a channel category.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `section_id` - ID of the section to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.delete_section(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
        "01965f7a-0000-7000-8000-000000000011",
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.add_content_to_category"></a>

#### add\_content\_to\_category

```python
async def add_content_to_category(
    channel_id: str,
    category_id: str,
    section_id: str,
    *,
    contents_ids: builtins.list[str]
) -> None
```

Add content items to a category section.

**Arguments**:

- `channel_id` - ID of the channel.
- `category_id` - ID of the category.
- `section_id` - ID of the section.
- `contents_ids` - List of content IDs to add.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.channels.add_content_to_category(
        "01965f7a-0000-7000-8000-000000000003",
        "01965f7a-0000-7000-8000-000000000004",
        "01965f7a-0000-7000-8000-000000000011",
        contents_ids=["01965f7a-0000-7000-8000-000000000005"],
    )
```
<a id="srg.resources.channels.AsyncChannelsResource.get_v2"></a>

#### get\_v2

```python
async def get_v2(channel_id: str) -> HubProfileChannelV2
```

Get detailed channel data by ID (v2).

**Arguments**:

- `channel_id` - ID of the channel to retrieve.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channel = await client.channels.get_v2(
        "01965f7a-0000-7000-8000-000000000003"
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
<a id="srg.resources.channels.AsyncChannelsResource.get_by_name_v2"></a>

#### get\_by\_name\_v2

```python
async def get_by_name_v2(
    hub_profile_username: str,
    channel_name: str
) -> HubProfileChannelV2
```

Get detailed channel data by hub profile username and channel name (v2).

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile.
- `channel_name` - Name slug of the channel.
  

**Returns**:

  HubProfileChannelV2 with categories and heading content.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    channel = await client.channels.get_by_name_v2(
        "acme-academy", "onboarding"
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
<a id="srg.resources.channels.AsyncChannelsResource.get_category_v2"></a>

#### get\_category\_v2

```python
async def get_category_v2(
    hub_profile_username: str,
    channel_name: str,
    category_name: str
) -> CategoryWithHubProfile
```

Get category details by hub profile username, channel name, and category name (v2).

**Arguments**:

- `hub_profile_username` - Username / slug of the hub profile.
- `channel_name` - Name slug of the channel.
- `category_name` - Name slug of the category.
  

**Returns**:

  CategoryWithHubProfile containing category details and hub
  profile context.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    category = await client.channels.get_category_v2(
        "acme-academy",
        "onboarding",
        "week-1",
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