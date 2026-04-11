"""Shared helpers for uploading images to S3 pre-signed URLs.

SRG uses S3-compatible storage exclusively.  A signed upload URL is obtained
from the API; the SDK then PUTs the raw image bytes directly to that URL.
No SRG auth headers are sent — authentication is baked into the signed URL.

These helpers are intentionally free of any resource-specific logic so they
can be reused from hub_profiles, workspaces, assets, contents, etc.
"""

import mimetypes
from pathlib import Path

import httpx


def extension_from_source(source: str | Path) -> str:
    """Return the lowercase file extension (no leading dot) of a path or URL.

    Query strings are stripped before extraction so URLs like
    ``https://cdn.example.com/photo.jpg?v=2`` return ``"jpg"``.

    Args:
        source: A local file path or an ``http(s)://`` URL.

    Returns:
        Lowercase extension string, e.g. ``"jpg"``, ``"png"``, ``"webp"``.
        Returns an empty string if no extension can be found.
    """
    path_str = str(source).split("?")[0]
    return Path(path_str).suffix.lstrip(".").lower()


def _content_type(source: str | Path) -> str:
    guess, _ = mimetypes.guess_type(str(source).split("?")[0])
    return guess or "application/octet-stream"


def read_image_sync(source: str | Path) -> tuple[bytes, str]:
    """Read image bytes + content-type from a local path or external URL (sync).

    Args:
        source: Local file path or ``http(s)://`` URL.

    Returns:
        ``(bytes, content_type)`` tuple.

    Raises:
        httpx.HTTPStatusError: If fetching a remote URL fails.
    """
    image_str = str(source)
    if image_str.startswith(("http://", "https://")):
        with httpx.Client() as client:
            resp = client.get(image_str)
            resp.raise_for_status()
            return resp.content, resp.headers.get("content-type", _content_type(source))
    content = Path(source).read_bytes()
    return content, _content_type(source)


async def read_image_async(source: str | Path) -> tuple[bytes, str]:
    """Read image bytes + content-type from a local path or external URL (async).

    Args:
        source: Local file path or ``http(s)://`` URL.

    Returns:
        ``(bytes, content_type)`` tuple.

    Raises:
        httpx.HTTPStatusError: If fetching a remote URL fails.
    """
    image_str = str(source)
    if image_str.startswith(("http://", "https://")):
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_str)
            resp.raise_for_status()
            return resp.content, resp.headers.get("content-type", _content_type(source))
    content = Path(source).read_bytes()
    return content, _content_type(source)


def put_bytes_to_signed_url(
    signed_url: str,
    content: bytes,
    content_type: str,
    *,
    extra_headers: dict[str, str] | None = None,
) -> None:
    """PUT pre-read bytes to an S3 pre-signed URL (sync).

    Args:
        signed_url: The pre-signed S3 upload URL.
        content: Raw image bytes to upload.
        content_type: MIME type of the image.
        extra_headers: Additional headers (e.g. S3 metadata headers).

    Raises:
        httpx.HTTPStatusError: If the PUT returns a non-2xx response.
    """
    headers = {
        "Content-Length": str(len(content)),
        "Content-Type": content_type,
        **(extra_headers or {}),
    }
    with httpx.Client() as client:
        resp = client.put(signed_url, content=content, headers=headers)
        resp.raise_for_status()


async def put_bytes_to_signed_url_async(
    signed_url: str,
    content: bytes,
    content_type: str,
    *,
    extra_headers: dict[str, str] | None = None,
) -> None:
    """PUT pre-read bytes to an S3 pre-signed URL (async).

    Args:
        signed_url: The pre-signed S3 upload URL.
        content: Raw image bytes to upload.
        content_type: MIME type of the image.
        extra_headers: Additional headers (e.g. S3 metadata headers).

    Raises:
        httpx.HTTPStatusError: If the PUT returns a non-2xx response.
    """
    headers = {
        "Content-Length": str(len(content)),
        "Content-Type": content_type,
        **(extra_headers or {}),
    }
    async with httpx.AsyncClient() as client:
        resp = await client.put(signed_url, content=content, headers=headers)
        resp.raise_for_status()


def upload_to_signed_url(
    signed_url: str,
    image: str | Path,
    *,
    extra_headers: dict[str, str] | None = None,
) -> None:
    """Read and upload an image to an S3 pre-signed URL in one call (sync).

    Convenience wrapper around :func:`read_image_sync` +
    :func:`put_bytes_to_signed_url`.  Use the lower-level helpers directly
    when the bytes have already been read (e.g. in contents/assets where size
    must be sent to the API before the signed URL is issued).

    Args:
        signed_url: The pre-signed S3 upload URL returned by the API.
        image: Local file path or ``http(s)://`` URL.
        extra_headers: Additional headers merged into the PUT request.

    Raises:
        httpx.HTTPStatusError: If any HTTP request returns a non-2xx response.
    """
    content, content_type = read_image_sync(image)
    put_bytes_to_signed_url(
        signed_url, content, content_type, extra_headers=extra_headers
    )


async def upload_to_signed_url_async(
    signed_url: str,
    image: str | Path,
    *,
    extra_headers: dict[str, str] | None = None,
) -> None:
    """Read and upload an image to an S3 pre-signed URL in one call (async).

    Async counterpart of :func:`upload_to_signed_url`.

    Args:
        signed_url: The pre-signed S3 upload URL returned by the API.
        image: Local file path or ``http(s)://`` URL.
        extra_headers: Additional headers merged into the PUT request.

    Raises:
        httpx.HTTPStatusError: If any HTTP request returns a non-2xx response.
    """
    content, content_type = await read_image_async(image)
    await put_bytes_to_signed_url_async(
        signed_url, content, content_type, extra_headers=extra_headers
    )
