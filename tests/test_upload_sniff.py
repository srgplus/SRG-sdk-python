"""Image type/size sniffing used for covers from extension-less URLs."""

import struct

import pytest

from srg._upload import (
    image_content_type,
    resolve_image_extension,
    sniff_image_extension,
)
from srg._upload_multipart import get_image_dimensions_from_bytes

PNG = (
    b"\x89PNG\r\n\x1a\n"
    + b"\x00\x00\x00\x0dIHDR"
    + struct.pack(">II", 640, 480)
    + b"\x08\x02\x00\x00\x00"
    + b"\x00" * 16
)

# SOI, an APP0 segment, then SOF0 declaring height 1920 x width 1080.
JPEG = (
    b"\xff\xd8"
    + b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    + b"\xff\xc0\x00\x11\x08"
    + struct.pack(">HH", 1920, 1080)
    + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"
    + b"\xff\xd9"
)

WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 16


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (PNG, "png"),
        (JPEG, "jpg"),
        (WEBP, "webp"),
        (b"GIF89a" + b"\x00" * 20, "gif"),
        (b"\x00\x00\x00\x18ftypheic" + b"\x00" * 20, "heic"),
        (b"plain text, not an image", None),
    ],
)
def test_sniff_image_extension(data: bytes, expected: str | None) -> None:
    assert sniff_image_extension(data) == expected


def test_magic_bytes_win_over_misleading_url_suffix() -> None:
    assert resolve_image_extension(PNG, "https://cdn.example/cover.jpg") == "png"


def test_extensionless_url_falls_back_to_content_type() -> None:
    blob = b"\x00" * 32  # unrecognised bytes
    assert (
        resolve_image_extension(blob, "https://r2.example/assets/abc", "image/webp")
        == "webp"
    )


def test_path_suffix_used_when_bytes_unknown() -> None:
    assert resolve_image_extension(b"\x00" * 32, "/tmp/cover.jpeg") == "jpeg"


def test_unknown_everything_returns_empty() -> None:
    assert resolve_image_extension(b"\x00" * 32, "https://x.example/blob", None) == ""


def test_dimensions_from_bytes() -> None:
    assert get_image_dimensions_from_bytes(PNG) == (640.0, 480.0)
    assert get_image_dimensions_from_bytes(JPEG) == (1080.0, 1920.0)


def test_image_content_type_matches_backend_mapping() -> None:
    # The signed cover PUT is bound to this MIME (backend FileHelper.GetContentType).
    assert image_content_type("jpg") == "image/jpeg"
    assert image_content_type("jpeg") == "image/jpeg"
    assert image_content_type("png") == "image/png"
    assert image_content_type("heic") == "image/heic"
    assert image_content_type("xyz", "application/x-thing") == "application/x-thing"
