## Asset

*model* `Asset(id, name, cover=None)`

Base asset response. The actual type is indicated by the $type field

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.

## AssetSearch

*model* `AssetSearch(id, name, type=None, cover=None, status=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **type** (*str | None, optional*) – Defaults to `None`.
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **status** (*str | None, optional*) – Defaults to `None`.

## AssetUploadSignedUrl

*model* `AssetUploadSignedUrl(id, cover_signed_url=None, cover_extension=None, metadata_headers=None)`

**Fields**

- **id** (*str*)
- **cover_signed_url** (*SignedUrl | None, optional*) – Defaults to `None`.
- **cover_extension** (*str | None, optional*) – Defaults to `None`.
- **metadata_headers** (*dict[str, str] | None, optional*) – Defaults to `None`.

## Embed

*model* `Embed(id, name, cover=None, duration_in_seconds=None, url, iframe_url=None)`

$type == 'Embed'

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **duration_in_seconds** (*float | None, optional*) – Defaults to `None`.
- **url** (*str*)
- **iframe_url** (*str | None, optional*) – Defaults to `None`.

## EmbedAssetCreate

*model* `EmbedAssetCreate(dollar_type='Embed', name, url, duration_in_seconds=None)`

$type == 'Embed'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Embed'`.
- **name** (*str*)
- **url** (*str*)
- **duration_in_seconds** (*float | None, optional*) – Defaults to `None`.

## File

*model* `File(id, name, cover=None, file_type, extension, memory_size_in_bytes, url, read_only=False)`

$type == 'File'

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **file_type** (*str*)
- **extension** (*str*)
- **memory_size_in_bytes** (*int*)
- **url** (*str*)
- **read_only** (*bool, optional*) – Defaults to `False`.

## FileAssetCreate

*model* `FileAssetCreate(dollar_type='File', name, extension, memory_size_in_bytes, read_only=False)`

$type == 'File'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'File'`.
- **name** (*str*)
- **extension** (*str*)
- **memory_size_in_bytes** (*int*)
- **read_only** (*bool, optional*) – Defaults to `False`.

## ImageAssetCreate

*model* `ImageAssetCreate(dollar_type='Image', name, extension, width, height, memory_size_in_bytes)`

$type == 'Image'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Image'`.
- **name** (*str*)
- **extension** (*str*)
- **width** (*float*)
- **height** (*float*)
- **memory_size_in_bytes** (*int*)

## ImageMedia

*model* `ImageMedia(id, name, cover=None, file_type, extension, memory_size_in_bytes, url, read_only=False, width, height)`

$type == 'Image'

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **file_type** (*str*)
- **extension** (*str*)
- **memory_size_in_bytes** (*int*)
- **url** (*str*)
- **read_only** (*bool, optional*) – Defaults to `False`.
- **width** (*float*)
- **height** (*float*)

## Media

*model* `Media(id, name, cover=None, duration_in_seconds=None, hls_stream_url=None, status, memory_size_in_bytes=None)`

$type == 'Media'

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **duration_in_seconds** (*float | None, optional*) – Defaults to `None`.
- **hls_stream_url** (*str | None, optional*) – Defaults to `None`.
- **status** (*str*)
- **memory_size_in_bytes** (*int | None, optional*) – Defaults to `None`.

## MediaAssetCreate

*model* `MediaAssetCreate(dollar_type='Media', name, duration_in_seconds=None, memory_size_in_bytes=None)`

$type == 'Media'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Media'`.
- **name** (*str*)
- **duration_in_seconds** (*float | None, optional*) – Defaults to `None`.
- **memory_size_in_bytes** (*int | None, optional*) – Defaults to `None`.

## PlayableAsset

*model* `PlayableAsset(id, name, cover=None, duration_in_seconds=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **duration_in_seconds** (*float | None, optional*) – Defaults to `None`.

## Video

*model* `Video(id, name, cover=None, file_type, extension, memory_size_in_bytes, url, read_only=False, hls_stream_url=None, status='')`

$type == 'Video'

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*AssetCover | None, optional*) – Defaults to `None`.
- **file_type** (*str*)
- **extension** (*str*)
- **memory_size_in_bytes** (*int*)
- **url** (*str*)
- **read_only** (*bool, optional*) – Defaults to `False`.
- **hls_stream_url** (*str | None, optional*) – Defaults to `None`.
- **status** (*str, optional*) – Defaults to `''`.

## VideoAssetCreate

*model* `VideoAssetCreate(dollar_type='Video', name, extension, memory_size_in_bytes)`

$type == 'Video'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'Video'`.
- **name** (*str*)
- **extension** (*str*)
- **memory_size_in_bytes** (*int*)

## parse_asset_response

```python
def parse_asset_response(
    data: dict[str, Any],
) -> Union[Media, Embed, Video, ImageMedia, File, Asset]
```

Deserialize an asset response dispatching on the $type discriminator.

