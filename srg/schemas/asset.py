import warnings
from typing import Any, Union

from pydantic import Field, model_validator

from srg.schemas.common import (
    AssetCover,
    SignedUrl,
    SRGModel,
)


class _AssetCreateBase(SRGModel):
    """Shared bits for asset-create payloads.

    Accepts the legacy ``dollar_type=`` kwarg with a DeprecationWarning so
    older callers keep working; new code should pass ``type=`` (or rely on
    the per-subclass default).
    """

    @model_validator(mode="before")
    @classmethod
    def _migrate_dollar_type(cls, data: Any) -> Any:
        if isinstance(data, dict) and "dollar_type" in data:
            warnings.warn(
                "`dollar_type` is deprecated; use `type` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            data.setdefault("$type", data.pop("dollar_type"))
        return data


class Asset(SRGModel):
    """
    Base asset response. The actual type is indicated by the $type field
    """

    id: str
    name: str
    cover: AssetCover | None = None


class PlayableAsset(Asset):
    duration_in_seconds: float | None = None


class Media(PlayableAsset):
    """$type == 'Media'"""

    hls_stream_url: str | None = None
    status: str
    memory_size_in_bytes: int | None = None


class Embed(PlayableAsset):
    """$type == 'Embed'"""

    url: str
    iframe_url: str | None = None


class File(Asset):
    """$type == 'File'"""

    file_type: str
    extension: str
    memory_size_in_bytes: int
    url: str
    read_only: bool = False


class Video(File):
    """$type == 'Video'"""

    hls_stream_url: str | None = None
    status: str = ""


class ImageMedia(File):
    """$type == 'Image'"""

    width: float
    height: float


AnyAssetResponse = Union[Media, Embed, Video, ImageMedia, File, Asset]


def parse_asset_response(data: dict[str, Any]) -> AnyAssetResponse:
    """Deserialize an asset response dispatching on the $type discriminator."""
    t = data.get("$type", "")
    dispatch: dict[str, type[Asset]] = {
        "Media": Media,
        "Embed": Embed,
        "Video": Video,
        "Image": ImageMedia,
        "File": File,
    }
    cls = dispatch.get(t, Asset)
    return cls.model_validate(data)


class AssetSearch(SRGModel):
    id: str
    name: str
    type: str | None = None
    cover: AssetCover | None = None
    status: str | None = None


class AssetUploadSignedUrl(SRGModel):
    id: str
    cover_signed_url: SignedUrl | None = None
    cover_extension: str | None = None
    metadata_headers: dict[str, str] | None = None


class MediaAssetCreate(_AssetCreateBase):
    """$type == 'Media'"""

    type: str = Field("Media", alias="$type")
    name: str
    extension: str | None = None
    duration_in_seconds: float | None = None
    memory_size_in_bytes: int | None = None
    upload_part_size_in_bytes: int | None = None


class EmbedAssetCreate(_AssetCreateBase):
    """$type == 'Embed'"""

    type: str = Field("Embed", alias="$type")
    name: str
    url: str
    duration_in_seconds: float | None = None


class FileAssetCreate(_AssetCreateBase):
    """$type == 'File'"""

    type: str = Field("File", alias="$type")
    name: str
    extension: str
    memory_size_in_bytes: int
    upload_part_size_in_bytes: int | None = None
    read_only: bool = False


class ImageAssetCreate(_AssetCreateBase):
    """$type == 'Image'"""

    type: str = Field("Image", alias="$type")
    name: str
    extension: str
    width: float
    height: float
    memory_size_in_bytes: int
    upload_part_size_in_bytes: int | None = None


class VideoAssetCreate(_AssetCreateBase):
    """$type == 'Video'"""

    type: str = Field("Video", alias="$type")
    name: str
    extension: str
    memory_size_in_bytes: int
    media_type: int | None = None
    upload_part_size_in_bytes: int | None = None


AnyAssetCreate = Union[
    MediaAssetCreate,
    EmbedAssetCreate,
    FileAssetCreate,
    ImageAssetCreate,
    VideoAssetCreate,
]


class AssetUploadInit(SRGModel):
    """Response from ``POST /api/v1/assets/batch``.

    Contains the asset id (``id``), the storage-side multipart upload id
    (``upload_id``), and the list of presigned PUT URLs — one per part.
    """

    id: str
    upload_id: str
    urls: list[str]
    type: str = Field(alias="$type")


class _CompleteUploadPartTag(SRGModel):
    """Single part tag for ``POST /api/v1/files/upload/complete``."""

    part_number: str
    e_tag: str = Field(alias="eTag")


class CompleteUploadRequest(SRGModel):
    """Payload for ``POST /api/v1/files/upload/complete``."""

    node_id: str
    upload_id: str
    part_tags: list[_CompleteUploadPartTag]


class AbortUploadRequest(SRGModel):
    """Payload for ``POST /api/v1/files/upload/abort``."""

    node_id: str
    upload_id: str
