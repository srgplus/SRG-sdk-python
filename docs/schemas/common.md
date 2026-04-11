## AssetCover

*model* `AssetCover(width, height, extension, size, modified, urls)`

**Fields**

- **width** (*float*)
- **height** (*float*)
- **extension** (*str | None*)
- **size** (*int*)
- **modified** (*datetime | None*)
- **urls** (*CoverUrls | None*)

## ContentCover

*model* `ContentCover(urls=None, extension=None, modified=None)`

Cover returned inside a ContentResponse.

**Fields**

- **urls** (*CoverUrls | None, optional*) – Defaults to `None`.
- **extension** (*str | None, optional*) – Defaults to `None`.
- **modified** (*datetime | None, optional*) – Defaults to `None`.

## ContentFileUploadParameters

*model* `ContentFileUploadParameters(image=None, generate_signed_url=True)`

Used in Content/Asset update to signal a cover change.

**Fields**

- **image** (*ImageUpsert | None, optional*) – Defaults to `None`.
- **generate_signed_url** (*bool, optional*) – Defaults to `True`.

## Cover

*model* `Cover(details, modified)`

**Fields**

- **details** (*CoverDetails | None*)
- **modified** (*datetime | None*)

## CoverDetails

*model* `CoverDetails(url, extension)`

**Fields**

- **url** (*str*)
- **extension** (*str*)

## CoverUrls

*model* `CoverUrls(original=None, thumbnail_large=None, thumbnail_small=None, large=None, blurred_large=None, seo=None)`

**Fields**

- **original** (*str | None, optional*) – Defaults to `None`.
- **thumbnail_large** (*str | None, optional*) – Defaults to `None`.
- **thumbnail_small** (*str | None, optional*) – Defaults to `None`.
- **large** (*str | None, optional*) – Defaults to `None`.
- **blurred_large** (*str | None, optional*) – Defaults to `None`.
- **seo** (*str | None, optional*) – Defaults to `None`.

## CursorPagedList

*model* `CursorPagedList(items, cursor=None)`

**Fields**

- **items** (*list[~T]*)
- **cursor** (*str | None, optional*) – Defaults to `None`.

## FileUploadParameters

*model* `FileUploadParameters(extension=None, generate_signed_url=True)`

Used in HubProfile update to signal a cover/avatar change.

**Fields**

- **extension** (*str | None, optional*) – Defaults to `None`.
- **generate_signed_url** (*bool, optional*) – Defaults to `True`.

## ImageUpsert

*model* `ImageUpsert(width, height, size, extension)`

Dimensions and metadata for a cover image to be uploaded.

**Fields**

- **width** (*int*)
- **height** (*int*)
- **size** (*int*)
- **extension** (*str*)

## SignedUrl

*model* `SignedUrl(url)`

**Fields**

- **url** (*str*)

## async_paginate

```python
def async_paginate(
    fetch: Callable[[str | None], Awaitable[CursorPagedList]],
) -> AsyncIterator[~T]
```

Async iterate through all pages of a cursor-paginated endpoint.

Example::

    from srg_sdk import async_paginate

    async for content in async_paginate(
        lambda cursor: client.contents.filter(
            hub_profile_id="...", page_size=50, cursor=cursor
        )
    ):
        print(content.name)


## paginate

```python
def paginate(fetch: Callable[[str | None], CursorPagedList]) -> Iterator[~T]
```

Iterate through all pages of a cursor-paginated endpoint.

Example::

    from srg_sdk import paginate

    for content in paginate(
        lambda cursor: client.contents.filter(
            hub_profile_id="...", page_size=50, cursor=cursor
        )
    ):
        print(content.name)

