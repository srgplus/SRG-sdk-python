from typing import Any

from pydantic import Field

from srg.schemas.common import SRGModel


class ViewOptionsUpsert(SRGModel):
    type: str | None = None


class ProgressionOptionsUpsert(SRGModel):
    enabled: bool = False


class CoverOptionsUpsert(SRGModel):
    show: bool = True


class ChannelCategoryOptionsUpsert(SRGModel):
    view: ViewOptionsUpsert = Field(default_factory=ViewOptionsUpsert)
    progression: ProgressionOptionsUpsert = Field(
        default_factory=ProgressionOptionsUpsert
    )
    cover: CoverOptionsUpsert = Field(default_factory=CoverOptionsUpsert)
    expandable: bool = True


class ChannelCategoryOptions(SRGModel):
    view: dict | None = None
    progression: dict | None = None
    cover: dict | None = None
    expandable: bool = True


class SectionBaseCreate(SRGModel):
    dollar_type: str = Field(alias="$type")
    name: str
    reference_ids: list[str] = Field(default_factory=list)


class CategoryToReorder(SRGModel):
    id: str
    order: int | None = None


class Section(SRGModel):
    id: str
    name: str | None = None
    cursor: str | None = None
    is_empty: bool = False
    type: str | None = None


class Category(SRGModel):
    id: str
    name: str
    is_archived: bool = False
    is_pinned: bool = False
    notifications_enabled: bool = True
    sections: list[Section] = Field(default_factory=list)
    options: ChannelCategoryOptions | None = None


class Channel(SRGModel):
    id: str
    name: str
    categories: list[Category] = Field(default_factory=list)


class HubProfileChannel(SRGModel):
    """Channel response returned by GET /api/v1/channels (list endpoint)."""

    id: str
    name: str
    privacy: str | None = None
    hub_profile_id: str | None = None
    hub_profile_name: str | None = None
    hub_profile_user_name: str | None = None
    is_archived: bool = False
    can_edit: bool = False
    can_archive: bool = False
    can_manage: bool = False
    categories: list[Category] = Field(default_factory=list)


class OrderedContentToCategoryReference(SRGModel):
    content_id: str
    section_id: str | None = None
    order: int | None = None


class ProgressionOptions(SRGModel):
    progression: bool = False
    sequential_completion: bool = False


class ViewOptions(SRGModel):
    presentation: Any | None = None


class CoverOptions(SRGModel):
    aspect: Any | None = None


class ChannelCategoryOptionsV2(SRGModel):
    expandable: bool = True
    view: ViewOptions | None = None
    cover: CoverOptions | None = None
    progression: ProgressionOptions | None = None


class CategoryHeadingContent(SRGModel):
    """Paginated heading content inside a v2 category."""

    references: list[Any] = Field(default_factory=list)
    total_count: int = 0
    next_cursor: str | None = None
    has_next: bool = False


class CategoryWithHeadingContent(SRGModel):
    """Category shape returned inside HubProfileChannelV2Response."""

    id: str
    name: str
    is_archived: bool = False
    is_pinned: bool = False
    notifications_enabled: bool = False
    sections: list[Section] = Field(default_factory=list)
    options: ChannelCategoryOptionsV2 | None = None
    heading_content: CategoryHeadingContent | None = None


class HubProfileChannelV2(SRGModel):
    """GET /api/v2/channels/{channelId} or /{hubProfileUserName}/{channelName}"""

    id: str
    name: str
    privacy: str | None = None
    hub_profile_name: str | None = None
    hub_profile_user_name: str | None = None
    categories: list[CategoryWithHeadingContent] = Field(default_factory=list)


class CategoryWithHubProfile(SRGModel):
    """GET /api/v2/channels/{hubProfileUserName}/{channelName}/categories/{name}"""

    id: str
    name: str
    is_archived: bool = False
    is_pinned: bool = False
    notifications_enabled: bool = False
    heading_content: CategoryHeadingContent | None = None
    hub_profile_id: str
    hub_profile_name: str | None = None
    hub_profile_user_name: str | None = None
