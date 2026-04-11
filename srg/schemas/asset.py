from typing import Any, Union

from pydantic import Field

from srg.schemas.common import (
    AssetCover,
    SignedUrl,
    SRGModel,
)


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


class MediaAssetCreate(SRGModel):
    """$type == 'Media'"""

    dollar_type: str = Field("Media", alias="$type")
    name: str
    duration_in_seconds: float | None = None
    memory_size_in_bytes: int | None = None


class EmbedAssetCreate(SRGModel):
    """$type == 'Embed'"""

    dollar_type: str = Field("Embed", alias="$type")
    name: str
    url: str
    duration_in_seconds: float | None = None


class FileAssetCreate(SRGModel):
    """$type == 'File'"""

    dollar_type: str = Field("File", alias="$type")
    name: str
    extension: str
    memory_size_in_bytes: int
    read_only: bool = False


class ImageAssetCreate(SRGModel):
    """$type == 'Image'"""

    dollar_type: str = Field("Image", alias="$type")
    name: str
    extension: str
    width: float
    height: float
    memory_size_in_bytes: int


class VideoAssetCreate(SRGModel):
    """$type == 'Video'"""

    dollar_type: str = Field("Video", alias="$type")
    name: str
    extension: str
    memory_size_in_bytes: int


AnyAssetCreate = Union[
    MediaAssetCreate,
    EmbedAssetCreate,
    FileAssetCreate,
    ImageAssetCreate,
    VideoAssetCreate,
]
