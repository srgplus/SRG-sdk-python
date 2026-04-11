from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

ContentPrivacy = Literal["Preview", "Private", "Public"]
ChannelPrivacy = Literal["Private", "Public"]
AvailabilityLevel = Literal["Public", "Private"]
ProgressionStatus = Literal["NotStarted", "Incomplete", "Completed"]

T = TypeVar("T")


class SRGModel(BaseModel):
    """
    Base model for all SRG SDK models.

    JSON keys use camelCase (matching ASP.NET Core defaults).
    Python attributes use snake_case.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class SignedUrl(SRGModel):
    url: str


class CoverDetails(SRGModel):
    url: str
    extension: str


class Cover(SRGModel):
    details: CoverDetails | None
    modified: datetime | None


class CoverUrls(SRGModel):
    original: str | None = None
    thumbnail_large: str | None = None
    thumbnail_small: str | None = None
    large: str | None = None
    blurred_large: str | None = None
    seo: str | None = None


class AssetCover(SRGModel):
    width: float
    height: float
    extension: str | None
    size: int
    modified: datetime | None
    urls: CoverUrls | None


class ContentCover(SRGModel):
    """Cover returned inside a ContentResponse."""

    urls: CoverUrls | None = None
    extension: str | None = None
    modified: datetime | None = None


class CursorPagedList(SRGModel, Generic[T]):
    items: list[T]
    cursor: str | None = None


class ImageUpsert(SRGModel):
    """Dimensions and metadata for a cover image to be uploaded."""

    width: int
    height: int
    size: int
    extension: str


class FileUploadParameters(SRGModel):
    """Used in HubProfile update to signal a cover/avatar change."""

    extension: str | None = None
    generate_signed_url: bool = True


class ContentFileUploadParameters(SRGModel):
    """Used in Content/Asset update to signal a cover change."""

    image: ImageUpsert | None = None
    generate_signed_url: bool = True


def paginate(
    fetch: Callable[[str | None], CursorPagedList[T]],
) -> Iterator[T]:
    """
    Iterate through all pages of a cursor-paginated endpoint.

    Example::

        from srg_sdk import paginate

        for content in paginate(
            lambda cursor: client.contents.filter(
                hub_profile_id="...", page_size=50, cursor=cursor
            )
        ):
            print(content.name)
    """
    cursor: str | None = None
    while True:
        page = fetch(cursor)
        yield from page.items
        if page.cursor is None:
            break
        cursor = page.cursor


async def async_paginate(
    fetch: Callable[[str | None], Awaitable[CursorPagedList[T]]],
) -> AsyncIterator[T]:
    """
    Async iterate through all pages of a cursor-paginated endpoint.

    Example::

        from srg_sdk import async_paginate

        async for content in async_paginate(
            lambda cursor: client.contents.filter(
                hub_profile_id="...", page_size=50, cursor=cursor
            )
        ):
            print(content.name)
    """
    cursor: str | None = None
    while True:
        page = await fetch(cursor)
        for item in page.items:
            yield item
        if page.cursor is None:
            break
        cursor = page.cursor
