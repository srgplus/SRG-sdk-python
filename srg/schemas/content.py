from datetime import datetime
from typing import Any

from pydantic import Field

from srg.schemas.common import (
    ContentCover,
    SignedUrl,
    SRGModel,
)


class TextWidgetCreate(SRGModel):
    dollar_type: str = Field("Text", alias="$type")
    title: str | None = None
    content: str


class MediaWidgetCreate(SRGModel):
    dollar_type: str = Field("Media", alias="$type")
    title: str | None = None
    asset_id: str
    autoplay: bool = False


class HubProfileWidgetCreate(SRGModel):
    dollar_type: str = Field("HubProfile", alias="$type")
    title: str | None = None
    hub_profile_id: str


class ContentWidgetCreate(SRGModel):
    dollar_type: str = Field("ContentWidget", alias="$type")
    title: str | None = None
    content_id: str
    # SRGDEV-520: optional display options for the widget (same wire shape as a
    # category's options, minus progression). Omit to use the server default. Shape:
    #   {
    #     "expandable": bool,                                  # needs a title to take effect
    #     "cover": {"aspect": {"ratio": {"position": str, "ratio": str}}},
    #     "view": {"presentation": {
    #        "$type": "Custom",
    #        "main": {"type": "Classic|List|Waterfall", "subType": "Extended|Compact"},
    #        "expanded": {"type": "Waterfall"}}},
    #   }
    # subType Extended = large cards, Compact = small cards.
    options: dict[str, Any] | None = None


class CustomLinkCreate(SRGModel):
    dollar_type: str = Field("CustomLink", alias="$type")
    # Backend LinkBaseCreate requires `title` + `url` on BOTH link kinds
    # (NOT `label`/`type`). title is 1-100 chars and unique within a LinkList.
    # `extension` (optional) is a CustomLink-only image extension.
    title: str
    url: str
    extension: str | None = None


class KnownLinkCreate(SRGModel):
    dollar_type: str = Field("KnownLink", alias="$type")
    title: str
    url: str


class LinkListCreate(SRGModel):
    dollar_type: str = Field("LinkList", alias="$type")
    title: str | None = None
    links: list[Any] = Field(
        default_factory=list
    )  # list[CustomLinkCreate | KnownLinkCreate]


AnyWidgetCreate = Any  # TextWidgetCreate | MediaWidgetCreate | LinkListCreate | ...


class ContentChannelUpsert(SRGModel):
    channel_id: str
    category_ids: list[str] = Field(default_factory=list)


class ContentChannelCategory(SRGModel):
    id: str
    name: str


class ContentChannel(SRGModel):
    id: str
    name: str
    categories: list[ContentChannelCategory] = Field(default_factory=list)


class OrderedContentCategoryReference(SRGModel):
    channel_id: str | None = None
    category_id: str | None = None
    order: int | None = None


class Content(SRGModel):
    id: str
    name: str
    details: str | None
    url: str | None
    created_by: str
    hub_profile_id: str
    hub_profile_name: str | None
    created: datetime
    archived: datetime | None
    cover: ContentCover | None
    channels: list[ContentChannel] = Field(default_factory=list)
    heading_referenced_content: list[OrderedContentCategoryReference] = Field(
        default_factory=list
    )


class ContentSearch(SRGModel):
    id: str
    name: str
    hub_profile_id: str | None = None
    cover: ContentCover | None = None
    privacy: str | None = None


class ContentUploadSignedUrl(SRGModel):
    id: str
    cover_signed_url: SignedUrl | None = None
    cover_extension: str | None = None
    context: list[Any] = Field(default_factory=list)
    metadata_headers: dict[str, str] | None = None


class ContentProgression(SRGModel):
    status: str | None = None


class CollectionProgressionStats(SRGModel):
    total: int = 0
    completed: int = 0


class MediaProgression(SRGModel):
    last_watched_time: int | None = None
    status: str | None = None


class MainPlayableAsset(SRGModel):
    """
    Polymorphic main asset ($type: Embed | Media | Video).

    All derived fields are optional so a single model handles all variants.
    """

    id: str
    name: str
    cover: ContentCover | None = None
    duration_in_seconds: int | None = None
    # Embed fields
    url: str | None = None
    iframe_url: str | None = None
    # Media / Video fields
    external_media_id: str | None = None
    hls_stream_url: str | None = None
    original_stream_url: str | None = None
    status: str | None = None
    progression: MediaProgression | None = None


class CollectionProgression(ContentProgression):
    total: int = 0
    completed: int = 0


class CreatedSection(SRGModel):
    id: str


class SubcontentSection(SRGModel):
    """Section that a subcontent item belongs to ($type: Section | SingleContentSection)."""

    dollar_type: str | None = Field(None, alias="$type")
    id: str
    cursor: str
    name: str | None = None


class SubcontentItem(SRGModel):
    """One subcontent item returned by GET /contents/{id}/{categoryName}/references.

    Polymorphic ($type: Content | Media | Embed | Image | Video | File).
    Common fields are mapped; type-specific fields are optional.
    """

    dollar_type: str | None = Field(None, alias="$type")
    id: str
    name: str
    cursor: str
    section: SubcontentSection
    created: datetime | None = None
    cover: ContentCover | None = None
    privacy: str | None = None
    preview_text: str | None = None
    progression: ContentProgression | None = None


class ContentV2(SRGModel):
    """GET /api/v2/contents/{contentId}"""

    id: str
    privacy: str
    name: str
    details: str | None = None
    url: str | None = None
    created_by: str
    hub_profile_id: str
    hub_profile_name: str | None = None
    main_asset: MainPlayableAsset | None = None
    context: list[Any] = Field(default_factory=list)
    created: datetime
    archived: datetime | None = None
    cover: ContentCover | None = None
    channels: list[ContentChannel] = Field(default_factory=list)
    categories: list[Any] = Field(default_factory=list)
    progression: ContentProgression | None = None
    tags: list[str] = Field(default_factory=list)
    ai_summary: str | None = None
