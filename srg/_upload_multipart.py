"""Multipart upload helpers for SRG asset uploads.

The SRG asset upload flow is a 3-step process:

1. ``POST /api/v1/assets/batch`` — create the asset and obtain a list of
   presigned PUT URLs (one per part) plus an ``uploadId``.
2. PUT each part of the file to its corresponding presigned URL. Each PUT
   returns an ``ETag`` header that must be collected.
3. ``POST /api/v1/files/upload/complete`` — finalize the upload by sending
   the collected part numbers + ETags back to SRG (NOT directly to S3).

Helpers in this module cover step 2 (parallel PUT of parts and ETag
collection). Step 1 is a regular create; step 3 is a regular SRG endpoint
call. Both live in ``srg.resources.assets``.

Part-size selection mirrors the iOS client (``MediaUploadsManager``):
5 MB minimum, dynamic target part count keyed on file size, capped at S3's
10 000-part limit.
"""

from __future__ import annotations

import asyncio
import struct
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import httpx

_MIN_PART_SIZE = 5 * 1024 * 1024  # 5 MB — S3 multipart minimum
_S3_MAX_PARTS = 10_000


def calculate_upload_part_size(file_size: int) -> int:
    """Pick a part size for an SRG multipart upload.

    Mirrors ``MediaUploadsManager.calculateUploadPartSize`` in the iOS app:
    floors at 5 MB and scales the target part count with file size.
    """
    if file_size <= _MIN_PART_SIZE:
        return _MIN_PART_SIZE

    if file_size < 100 * 1024 * 1024:  # < 100 MB
        target_parts = max(1, file_size // _MIN_PART_SIZE)
    elif file_size < 1024 * 1024 * 1024:  # 100 MB – 1 GB
        target_parts = 50
    elif file_size < 10 * 1024 * 1024 * 1024:  # 1 GB – 10 GB
        target_parts = 100
    else:
        target_parts = 200

    proposed = (file_size + target_parts - 1) // target_parts
    required = (file_size + _S3_MAX_PARTS - 1) // _S3_MAX_PARTS
    return max(_MIN_PART_SIZE, proposed, required)


PartTag = tuple[int, str]
"""``(part_number, etag)`` — ``part_number`` is 1-based."""

ProgressCallback = Callable[[int, int], None]
"""``(bytes_uploaded, total_bytes)``. Called from upload threads/tasks."""


def _read_part(file_path: str | Path, offset: int, length: int) -> bytes:
    with open(file_path, "rb") as f:
        f.seek(offset)
        return f.read(length)


def _strip_etag(raw: str) -> str:
    return raw.strip().strip('"')


def upload_parts_sync(
    file_path: str | Path,
    urls: list[str],
    *,
    part_size: int,
    file_size: int,
    on_progress: ProgressCallback | None = None,
    max_workers: int = 5,
    timeout_seconds: float = 300.0,
) -> list[PartTag]:
    """PUT each chunk of ``file_path`` to its presigned URL in parallel (sync).

    Returns the list of ``(part_number, etag)`` tuples sorted by part number.
    Raises ``httpx.HTTPStatusError`` if any PUT fails.
    """
    if len(urls) == 0:
        raise ValueError("urls must not be empty")

    progress_lock = Lock()
    uploaded = [0]

    def upload_one(part_index: int, url: str) -> PartTag:
        offset = part_index * part_size
        length = min(part_size, file_size - offset)
        data = _read_part(file_path, offset, length)

        with httpx.Client(timeout=timeout_seconds) as client:
            resp = client.put(
                url,
                content=data,
                headers={
                    "Content-Length": str(len(data)),
                    "Content-Type": "application/octet-stream",
                },
            )
            resp.raise_for_status()
            etag = _strip_etag(resp.headers.get("ETag", ""))

        if on_progress is not None:
            with progress_lock:
                uploaded[0] += len(data)
                on_progress(uploaded[0], file_size)

        return (part_index + 1, etag)

    results: list[PartTag] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(upload_one, i, url) for i, url in enumerate(urls)]
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda x: x[0])
    return results


async def upload_parts_async(
    file_path: str | Path,
    urls: list[str],
    *,
    part_size: int,
    file_size: int,
    on_progress: ProgressCallback | None = None,
    max_concurrency: int = 5,
    timeout_seconds: float = 300.0,
) -> list[PartTag]:
    """Async counterpart of :func:`upload_parts_sync`."""
    if len(urls) == 0:
        raise ValueError("urls must not be empty")

    semaphore = asyncio.Semaphore(max_concurrency)
    uploaded = 0
    lock = asyncio.Lock()

    async def upload_one(
        client: httpx.AsyncClient, part_index: int, url: str
    ) -> PartTag:
        nonlocal uploaded
        offset = part_index * part_size
        length = min(part_size, file_size - offset)
        data = await asyncio.to_thread(_read_part, file_path, offset, length)

        async with semaphore:
            resp = await client.put(
                url,
                content=data,
                headers={
                    "Content-Length": str(len(data)),
                    "Content-Type": "application/octet-stream",
                },
            )
            resp.raise_for_status()
            etag = _strip_etag(resp.headers.get("ETag", ""))

        if on_progress is not None:
            async with lock:
                uploaded += len(data)
                on_progress(uploaded, file_size)

        return (part_index + 1, etag)

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        results = await asyncio.gather(
            *(upload_one(client, i, u) for i, u in enumerate(urls))
        )

    results = list(results)
    results.sort(key=lambda x: x[0])
    return results


def _ext(path: str | Path) -> str:
    return Path(str(path).split("?")[0]).suffix.lstrip(".").lower()


_IMAGE_EXTS = {"jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "heic"}
_VIDEO_EXTS = {
    "4mv",
    "amv",
    "avi",
    "flv",
    "m4p",
    "m4v",
    "mkv",
    "mov",
    "mp3",
    "mp4",
    "mpeg",
    "mpg",
    "mxf",
    "ogg",
    "ts",
    "vod",
    "wav",
    "webm",
    "wmv",
}


def detect_asset_kind(file_path: str | Path) -> str:
    """Best-effort ``$type`` from a file extension. Defaults to ``"File"``."""
    ext = _ext(file_path)
    if ext in _IMAGE_EXTS:
        return "Image"
    if ext in _VIDEO_EXTS:
        return "Video"
    return "File"


def get_image_dimensions(file_path: str | Path) -> tuple[float, float] | None:
    """Read width/height from an image file. Returns ``None`` on failure.

    Tries a stdlib-only parser first (PNG, JPEG, GIF, BMP, WEBP) so the SDK
    works out of the box. Falls back to Pillow if installed (covers HEIC and
    other formats Pillow understands).
    """
    dims = _read_image_dimensions_stdlib(file_path)
    if dims is not None:
        return dims
    try:
        from PIL import Image  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        with Image.open(file_path) as img:
            w, h = img.size
            return float(w), float(h)
    except Exception:
        return None


def _read_image_dimensions_stdlib(
    file_path: str | Path,
) -> tuple[float, float] | None:
    """Parse width/height from common image headers without external deps.

    Supports PNG, JPEG (incl. progressive), GIF, BMP, and RIFF/WEBP (VP8/VP8L/
    VP8X). Returns ``None`` for unrecognised formats or malformed headers.
    """
    try:
        with open(file_path, "rb") as f:
            head = f.read(32)
            if len(head) < 16:
                return None

            # PNG: \x89PNG\r\n\x1a\n then IHDR with width/height as big-endian u32.
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                return float(w), float(h)

            # GIF87a / GIF89a: width/height as little-endian u16 at offset 6.
            if head[:6] in (b"GIF87a", b"GIF89a"):
                w, h = struct.unpack("<HH", head[6:10])
                return float(w), float(h)

            # BMP: width/height as little-endian i32 at offset 18.
            if head[:2] == b"BM":
                w, h = struct.unpack("<ii", head[18:26])
                return float(w), float(abs(h))

            # WEBP (RIFF container).
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                fourcc = head[12:16]
                if fourcc == b"VP8 ":
                    # bitstream starts at offset 20; width/height at +6, 14-bit LE.
                    f.seek(26)
                    buf = f.read(4)
                    if len(buf) == 4:
                        w = struct.unpack("<H", buf[0:2])[0] & 0x3FFF
                        h = struct.unpack("<H", buf[2:4])[0] & 0x3FFF
                        return float(w), float(h)
                if fourcc == b"VP8L":
                    f.seek(21)
                    buf = f.read(4)
                    if len(buf) == 4:
                        b0, b1, b2, b3 = buf
                        w = ((b1 & 0x3F) << 8 | b0) + 1
                        h = ((b3 & 0x0F) << 10 | b2 << 2 | (b1 & 0xC0) >> 6) + 1
                        return float(w), float(h)
                if fourcc == b"VP8X":
                    f.seek(24)
                    buf = f.read(6)
                    if len(buf) == 6:
                        w = (buf[0] | buf[1] << 8 | buf[2] << 16) + 1
                        h = (buf[3] | buf[4] << 8 | buf[5] << 16) + 1
                        return float(w), float(h)
                return None

            # JPEG: iterate markers until SOFn (0xC0..0xCF except 0xC4/0xC8/0xCC).
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    b = f.read(1)
                    while b == b"\xff":
                        b = f.read(1)
                    if not b:
                        return None
                    marker = b[0]
                    if marker in (0xD8, 0xD9):
                        return None
                    if marker == 0x00 or 0xD0 <= marker <= 0xD7:
                        continue
                    size_bytes = f.read(2)
                    if len(size_bytes) < 2:
                        return None
                    seg_len = struct.unpack(">H", size_bytes)[0]
                    if seg_len < 2:
                        return None
                    if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                        payload = f.read(seg_len - 2)
                        if len(payload) < 5:
                            return None
                        h, w = struct.unpack(">HH", payload[1:5])
                        return float(w), float(h)
                    f.seek(seg_len - 2, 1)
                    nxt = f.read(1)
                    if nxt != b"\xff":
                        return None
                    f.seek(-1, 1)
            return None
    except OSError:
        return None
