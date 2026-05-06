from __future__ import annotations

import struct
import warnings
import zlib
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
import respx

from srg._upload_multipart import (
    calculate_upload_part_size,
    detect_asset_kind,
    upload_parts_async,
    upload_parts_sync,
)
from srg.resources.assets import (
    AssetsResource,
    AssetUploadInput,
    AsyncAssetsResource,
    _resolve_input,
)
from srg.schemas.asset import (
    EmbedAssetCreate,
    FileAssetCreate,
    ImageAssetCreate,
    MediaAssetCreate,
    VideoAssetCreate,
)

HUB_PROFILE_ID = "hub-profile-uuid-1"
ASSET_ID = "asset-uuid-1"

MEDIA_ASSET_PAYLOAD = {
    "$type": "Media",
    "id": ASSET_ID,
    "name": "Intro Video",
    "hlsStreamUrl": None,
    "status": "pending_upload",
    "durationInSeconds": 120.0,
    "memorySizeInBytes": 52_428_800,
    "cover": None,
}

ASSET_UPLOAD_SIGNED_URL_PAYLOAD = {
    "id": ASSET_ID,
    "coverSignedUrl": None,
    "metadataHeaders": None,
}


class TestAssetsFilter:
    def test_filter_first_page(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        result = resource.filter(
            HUB_PROFILE_ID, page_size=20, workspace_id="workspace-uuid-1"
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["pageSize"] == 20
        assert body["onlyArchived"] is False
        assert result.items == []
        assert result.cursor is None

    def test_filter_with_cursor(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        resource.filter(
            HUB_PROFILE_ID, page_size=10, cursor="abc", workspace_id="workspace-uuid-1"
        )

        assert mock_http.post.call_args[1]["json"]["cursor"] == "abc"

    def test_filter_with_types(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        resource.filter(
            HUB_PROFILE_ID,
            page_size=10,
            types=["Media"],
            workspace_id="workspace-uuid-1",
        )

        assert mock_http.post.call_args[1]["json"]["type"] == ["Media"]


class TestAssetsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [
            {"id": str(i), "name": n, "$type": "Media"} for i, n in enumerate(names)
        ]
        return {"items": items, "cursor": cursor}

    def test_single_page_yields_all(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page(["Video A", "Video B"], cursor=None)
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1")
        )

        assert [r.name for r in result] == ["Video A", "Video B"]
        assert mock_http.post.call_count == 1

    def test_multiple_pages_yields_all(self, mock_http: Mock) -> None:
        pages = [
            self._page(["A", "B"], cursor="cur2"),
            self._page(["C"], cursor=None),
        ]
        mock_http.post.side_effect = pages
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1")
        )

        assert [r.name for r in result] == ["A", "B", "C"]
        assert mock_http.post.call_count == 2

    def test_cursor_passed_to_second_call(self, mock_http: Mock) -> None:
        pages = [
            self._page(["A"], cursor="next"),
            self._page(["B"], cursor=None),
        ]
        mock_http.post.side_effect = pages
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))

        first_body = mock_http.post.call_args_list[0][1]["json"]
        second_body = mock_http.post.call_args_list[1][1]["json"]
        assert "cursor" not in first_body
        assert second_body["cursor"] == "next"

    def test_default_page_size_is_50(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))

        assert mock_http.post.call_args[1]["json"]["pageSize"] == 50

    def test_empty_result(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        assert (
            list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))
            == []
        )


class TestAssetsSearchAll:
    def test_yields_all_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = [
            {"id": "1", "name": "Intro", "$type": "Media"},
            {"id": "2", "name": "Intro Final", "$type": "Media"},
        ]
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.search_all(
                HUB_PROFILE_ID, search="intro", workspace_id="workspace-uuid-1"
            )
        )

        assert [r.name for r in result] == ["Intro", "Intro Final"]
        assert mock_http.post.call_count == 1

    def test_empty_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        assert (
            list(
                resource.search_all(
                    HUB_PROFILE_ID, search="nothing", workspace_id="workspace-uuid-1"
                )
            )
            == []
        )


class TestAsyncAssetsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [
            {"id": str(i), "name": n, "$type": "Media"} for i, n in enumerate(names)
        ]
        return {"items": items, "cursor": cursor}

    async def test_single_page(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = self._page(["A", "B"], cursor=None)
        resource = AsyncAssetsResource({"workspace-uuid-1": async_mock_http})

        result = [
            item
            async for item in resource.filter_all(
                HUB_PROFILE_ID, workspace_id="workspace-uuid-1"
            )
        ]

        assert [r.name for r in result] == ["A", "B"]

    async def test_multiple_pages(self, async_mock_http: AsyncMock) -> None:
        pages = [
            self._page(["A", "B"], cursor="cur2"),
            self._page(["C"], cursor=None),
        ]
        async_mock_http.post.side_effect = pages
        resource = AsyncAssetsResource({"workspace-uuid-1": async_mock_http})

        result = [
            item
            async for item in resource.filter_all(
                HUB_PROFILE_ID, workspace_id="workspace-uuid-1"
            )
        ]

        assert [r.name for r in result] == ["A", "B", "C"]
        assert async_mock_http.post.call_count == 2

    async def test_search_all(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = [
            {"id": "1", "name": "Intro", "$type": "Media"},
        ]
        resource = AsyncAssetsResource({"workspace-uuid-1": async_mock_http})

        result = [
            item
            async for item in resource.search_all(
                HUB_PROFILE_ID, search="intro", workspace_id="workspace-uuid-1"
            )
        ]

        assert result[0].name == "Intro"


# ---------------------------------------------------------------------------
# Upload flow — schemas, helpers, end-to-end with mocked HTTP
# ---------------------------------------------------------------------------


def _make_test_png(width: int = 4, height: int = 4) -> bytes:
    """Tiny but valid PNG, no Pillow dependency."""

    def chunk(name: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    rows = b"".join(b"\x00" + bytes([255, 0, 0] * width) for _ in range(height))
    return (
        sig
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


@pytest.fixture
def png_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.png"
    p.write_bytes(_make_test_png())
    return p


@pytest.fixture
def text_file(tmp_path: Path) -> Path:
    p = tmp_path / "notes.txt"
    p.write_text("hello smoke test\n")
    return p


@pytest.fixture
def md_file(tmp_path: Path) -> Path:
    p = tmp_path / "readme.md"
    p.write_text("# Title\n\nbody\n")
    return p


@pytest.fixture
def big_file(tmp_path: Path) -> Path:
    """File large enough to require multiple multipart parts."""
    p = tmp_path / "big.bin"
    p.write_bytes(b"\xab" * (12 * 1024 * 1024))  # 12 MB → 3 parts at 5 MB each
    return p


class TestCalculateUploadPartSize:
    def test_below_minimum_returns_5mb(self) -> None:
        assert calculate_upload_part_size(0) == 5 * 1024 * 1024
        assert calculate_upload_part_size(1024) == 5 * 1024 * 1024
        assert calculate_upload_part_size(5 * 1024 * 1024) == 5 * 1024 * 1024

    def test_under_100mb_floors_at_5mb(self) -> None:
        # 60 MB → target_parts = 60MB // 5MB = 12; proposed = 5 MB
        assert calculate_upload_part_size(60 * 1024 * 1024) == 5 * 1024 * 1024

    def test_500mb_uses_50_target_parts(self) -> None:
        size = 500 * 1024 * 1024
        result = calculate_upload_part_size(size)
        # ceil(500 / 50) = 10 MB
        assert result == 10 * 1024 * 1024

    def test_5gb_uses_100_target_parts(self) -> None:
        size = 5 * 1024 * 1024 * 1024
        result = calculate_upload_part_size(size)
        # ceil(5GB / 100) = ~52.4 MB
        assert result >= 50 * 1024 * 1024

    def test_caps_under_s3_10000_part_limit(self) -> None:
        size = 100 * 1024 * 1024 * 1024  # 100 GB
        part = calculate_upload_part_size(size)
        n_parts = (size + part - 1) // part
        assert n_parts <= 10_000


class TestDetectAssetKind:
    def test_image_extensions(self) -> None:
        assert detect_asset_kind("a.png") == "Image"
        assert detect_asset_kind("a.JPG") == "Image"
        assert detect_asset_kind("/x/y/photo.webp") == "Image"

    def test_video_extensions(self) -> None:
        assert detect_asset_kind("clip.mp4") == "Video"
        assert detect_asset_kind("clip.MOV") == "Video"

    def test_other_extensions_default_to_file(self) -> None:
        assert detect_asset_kind("readme.md") == "File"
        assert detect_asset_kind("doc.pdf") == "File"
        assert detect_asset_kind("notes.txt") == "File"
        assert detect_asset_kind("noext") == "File"


class TestResolveInput:
    def test_text_file_resolves_as_file(self, text_file: Path) -> None:
        create, path, size, part = _resolve_input(AssetUploadInput(file=text_file))
        assert isinstance(create, FileAssetCreate)
        assert create.type == "File"
        assert create.extension == "txt"
        assert create.memory_size_in_bytes == size
        assert create.upload_part_size_in_bytes == part
        assert path == text_file

    def test_md_file_resolves_as_file(self, md_file: Path) -> None:
        create, _path, _size, _part = _resolve_input(AssetUploadInput(file=md_file))
        assert isinstance(create, FileAssetCreate)
        assert create.extension == "md"

    def test_image_explicit_dimensions(self, png_file: Path) -> None:
        create, _p, _s, _ps = _resolve_input(
            AssetUploadInput(file=png_file, width=4, height=4)
        )
        assert isinstance(create, ImageAssetCreate)
        assert create.width == 4
        assert create.height == 4
        assert create.extension == "png"

    def test_video_with_media_type(self, tmp_path: Path) -> None:
        v = tmp_path / "x.mp4"
        v.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"\x00" * 100)
        create, _p, _s, _ps = _resolve_input(AssetUploadInput(file=v, media_type=2))
        assert isinstance(create, VideoAssetCreate)
        assert create.media_type == 2
        assert create.extension == "mp4"

    def test_explicit_type_overrides_extension(self, text_file: Path) -> None:
        create, _p, _s, _ps = _resolve_input(
            AssetUploadInput(file=text_file, type="Video")
        )
        assert isinstance(create, VideoAssetCreate)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _resolve_input(AssetUploadInput(file=tmp_path / "nope"))

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.txt"
        empty.write_bytes(b"")
        with pytest.raises(ValueError, match="Empty file"):
            _resolve_input(AssetUploadInput(file=empty))

    def test_image_without_pillow_and_no_dimensions_raises(
        self, png_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Force the Pillow path to fail by making get_image_dimensions return None.
        monkeypatch.setattr(
            "srg.resources.assets.get_image_dimensions", lambda _p: None
        )
        with pytest.raises(ValueError, match="Image dimensions required"):
            _resolve_input(AssetUploadInput(file=png_file))


class TestUploadPartsSync:
    @respx.mock
    def test_uploads_each_part_and_returns_etags(self, big_file: Path) -> None:
        urls = [f"https://s3.example/part-{i}?sig=x" for i in range(3)]
        for i, url in enumerate(urls):
            respx.put(url).mock(
                return_value=httpx.Response(200, headers={"ETag": f'"etag-{i}"'})
            )

        size = big_file.stat().st_size
        part_size = calculate_upload_part_size(size)
        tags = upload_parts_sync(big_file, urls, part_size=part_size, file_size=size)

        assert [n for n, _ in tags] == [1, 2, 3]
        assert {e for _, e in tags} == {"etag-0", "etag-1", "etag-2"}

    @respx.mock
    def test_progress_callback_aggregates_to_total(self, big_file: Path) -> None:
        urls = [f"https://s3.example/part-{i}" for i in range(3)]
        for i, url in enumerate(urls):
            respx.put(url).mock(
                return_value=httpx.Response(200, headers={"ETag": f'"e{i}"'})
            )

        progress_log: list[tuple[int, int]] = []
        size = big_file.stat().st_size
        part_size = calculate_upload_part_size(size)
        upload_parts_sync(
            big_file,
            urls,
            part_size=part_size,
            file_size=size,
            on_progress=lambda u, t: progress_log.append((u, t)),
        )

        assert progress_log[-1] == (size, size)
        assert all(t == size for _, t in progress_log)


class TestUploadPartsAsync:
    @respx.mock
    async def test_async_uploads_each_part(self, big_file: Path) -> None:
        urls = [f"https://s3.example/part-{i}" for i in range(3)]
        for i, url in enumerate(urls):
            respx.put(url).mock(
                return_value=httpx.Response(200, headers={"ETag": f'"e{i}"'})
            )

        size = big_file.stat().st_size
        part_size = calculate_upload_part_size(size)
        tags = await upload_parts_async(
            big_file, urls, part_size=part_size, file_size=size
        )

        assert [n for n, _ in tags] == [1, 2, 3]


class TestUploadEndToEnd:
    """Full ``upload`` flow — init → PUT parts → complete → GET asset."""

    def _setup_init_and_complete(
        self,
        mock_http: Mock,
        *,
        nodes: list[tuple[str, str, list[str], str]],
        get_responses: list[dict],
    ) -> None:
        """Wire ``mock_http`` so the post sequence: init → complete[*] is right."""
        init_payload = [
            {"id": nid, "uploadId": uid, "urls": urls, "$type": kind}
            for (nid, uid, urls, kind) in nodes
        ]
        # init returns the list, every subsequent post (one per file) is complete
        mock_http.post.side_effect = [init_payload] + [None] * len(nodes)
        mock_http.get.side_effect = get_responses

    @respx.mock
    def test_upload_text_file(self, mock_http: Mock, text_file: Path) -> None:
        urls = ["https://s3.example/txt-part-0"]
        respx.put(urls[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"abc"'})
        )

        self._setup_init_and_complete(
            mock_http,
            nodes=[("node-1", "up-1", urls, "File")],
            get_responses=[
                {
                    "$type": "File",
                    "id": "node-1",
                    "name": "notes.txt",
                    "extension": "txt",
                    "memorySizeInBytes": text_file.stat().st_size,
                    "fileType": "text/plain",
                    "url": "https://cdn/notes.txt",
                    "readOnly": False,
                }
            ],
        )

        resource = AssetsResource({"workspace-uuid-1": mock_http})
        asset = resource.upload(
            hub_profile_id=HUB_PROFILE_ID,
            file=text_file,
            workspace_id="workspace-uuid-1",
        )

        assert asset.id == "node-1"
        # init body
        init_body = mock_http.post.call_args_list[0][1]["json"]
        assert init_body["hubProfileId"] == HUB_PROFILE_ID
        assert init_body["assets"][0]["$type"] == "File"
        assert init_body["assets"][0]["extension"] == "txt"
        assert "uploadPartSizeInBytes" in init_body["assets"][0]
        # complete body
        complete_call = mock_http.post.call_args_list[1]
        assert complete_call[0][0] == "/api/v1/files/upload/complete"
        complete_body = complete_call[1]["json"]
        assert complete_body["nodeId"] == "node-1"
        assert complete_body["uploadId"] == "up-1"
        assert complete_body["partTags"] == [{"partNumber": "1", "eTag": "abc"}]

    @respx.mock
    def test_upload_md_file(self, mock_http: Mock, md_file: Path) -> None:
        urls = ["https://s3.example/md-part-0"]
        respx.put(urls[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"md-tag"'})
        )

        self._setup_init_and_complete(
            mock_http,
            nodes=[("node-md", "up-md", urls, "File")],
            get_responses=[
                {
                    "$type": "File",
                    "id": "node-md",
                    "name": "readme.md",
                    "extension": "md",
                    "memorySizeInBytes": md_file.stat().st_size,
                    "fileType": "text/markdown",
                    "url": "https://cdn/readme.md",
                    "readOnly": False,
                }
            ],
        )

        resource = AssetsResource({"workspace-uuid-1": mock_http})
        asset = resource.upload(
            hub_profile_id=HUB_PROFILE_ID,
            file=md_file,
            workspace_id="workspace-uuid-1",
        )

        assert asset.id == "node-md"
        init_body = mock_http.post.call_args_list[0][1]["json"]
        assert init_body["assets"][0]["extension"] == "md"
        assert init_body["assets"][0]["$type"] == "File"

    @respx.mock
    def test_upload_image_with_explicit_dimensions(
        self, mock_http: Mock, png_file: Path
    ) -> None:
        urls = ["https://s3.example/img-part-0"]
        respx.put(urls[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"img"'})
        )
        self._setup_init_and_complete(
            mock_http,
            nodes=[("node-img", "up-img", urls, "Image")],
            get_responses=[
                {
                    "$type": "Image",
                    "id": "node-img",
                    "name": "test.png",
                    "extension": "png",
                    "memorySizeInBytes": png_file.stat().st_size,
                    "fileType": "image/png",
                    "url": "https://cdn/test.png",
                    "readOnly": False,
                    "width": 4,
                    "height": 4,
                }
            ],
        )

        resource = AssetsResource({"workspace-uuid-1": mock_http})
        asset = resource.upload(
            hub_profile_id=HUB_PROFILE_ID,
            file=png_file,
            width=4,
            height=4,
            workspace_id="workspace-uuid-1",
        )

        assert asset.id == "node-img"
        init_body = mock_http.post.call_args_list[0][1]["json"]
        assert init_body["assets"][0]["$type"] == "Image"
        assert init_body["assets"][0]["width"] == 4
        assert init_body["assets"][0]["height"] == 4

    @respx.mock
    def test_upload_multipart_assembles_parts_in_order(
        self, mock_http: Mock, big_file: Path
    ) -> None:
        urls = [f"https://s3.example/big-{i}" for i in range(3)]
        for i, u in enumerate(urls):
            respx.put(u).mock(
                return_value=httpx.Response(200, headers={"ETag": f'"e{i}"'})
            )

        self._setup_init_and_complete(
            mock_http,
            nodes=[("node-big", "up-big", urls, "File")],
            get_responses=[
                {
                    "$type": "File",
                    "id": "node-big",
                    "name": "big.bin",
                    "extension": "bin",
                    "memorySizeInBytes": big_file.stat().st_size,
                    "fileType": "application/octet-stream",
                    "url": "https://cdn/big.bin",
                    "readOnly": False,
                }
            ],
        )
        resource = AssetsResource({"workspace-uuid-1": mock_http})
        resource.upload(
            hub_profile_id=HUB_PROFILE_ID,
            file=big_file,
            workspace_id="workspace-uuid-1",
        )

        complete_body = mock_http.post.call_args_list[1][1]["json"]
        # Part numbers are 1-based and contiguous, ETags stripped of quotes
        assert [p["partNumber"] for p in complete_body["partTags"]] == ["1", "2", "3"]
        assert [p["eTag"] for p in complete_body["partTags"]] == ["e0", "e1", "e2"]

    @respx.mock
    def test_upload_failure_aborts(self, mock_http: Mock, text_file: Path) -> None:
        urls = ["https://s3.example/will-fail"]
        respx.put(urls[0]).mock(return_value=httpx.Response(500))

        # init then abort (no complete because PUT fails)
        mock_http.post.side_effect = [
            [{"id": "n1", "uploadId": "u1", "urls": urls, "$type": "File"}],
            None,  # abort
        ]

        resource = AssetsResource({"workspace-uuid-1": mock_http})
        with pytest.raises(httpx.HTTPStatusError):
            resource.upload(
                hub_profile_id=HUB_PROFILE_ID,
                file=text_file,
                workspace_id="workspace-uuid-1",
            )

        abort_call = mock_http.post.call_args_list[1]
        assert abort_call[0][0] == "/api/v1/files/upload/abort"
        assert abort_call[1]["json"] == {"nodeId": "n1", "uploadId": "u1"}


class TestUploadBatch:
    @respx.mock
    def test_batch_mixed_files(
        self,
        mock_http: Mock,
        text_file: Path,
        md_file: Path,
        png_file: Path,
    ) -> None:
        urls_a = ["https://s3.example/a"]
        urls_b = ["https://s3.example/b"]
        urls_c = ["https://s3.example/c"]
        respx.put(urls_a[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"ta"'})
        )
        respx.put(urls_b[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"tb"'})
        )
        respx.put(urls_c[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"tc"'})
        )

        init_payload = [
            {"id": "na", "uploadId": "ua", "urls": urls_a, "$type": "File"},
            {"id": "nb", "uploadId": "ub", "urls": urls_b, "$type": "File"},
            {"id": "nc", "uploadId": "uc", "urls": urls_c, "$type": "Image"},
        ]
        # init + 3 complete posts (one per file)
        mock_http.post.side_effect = [init_payload, None, None, None]
        mock_http.get.side_effect = [
            {
                "$type": "File",
                "id": "na",
                "name": "notes.txt",
                "extension": "txt",
                "memorySizeInBytes": 1,
                "fileType": "text/plain",
                "url": "https://cdn/a",
                "readOnly": False,
            },
            {
                "$type": "File",
                "id": "nb",
                "name": "readme.md",
                "extension": "md",
                "memorySizeInBytes": 1,
                "fileType": "text/markdown",
                "url": "https://cdn/b",
                "readOnly": False,
            },
            {
                "$type": "Image",
                "id": "nc",
                "name": "test.png",
                "extension": "png",
                "memorySizeInBytes": 1,
                "fileType": "image/png",
                "url": "https://cdn/c",
                "readOnly": False,
                "width": 4,
                "height": 4,
            },
        ]

        resource = AssetsResource({"workspace-uuid-1": mock_http})
        result = resource.upload_batch(
            hub_profile_id=HUB_PROFILE_ID,
            files=[
                AssetUploadInput(file=text_file),
                AssetUploadInput(file=md_file),
                AssetUploadInput(file=png_file, width=4, height=4),
            ],
            workspace_id="workspace-uuid-1",
        )

        assert [a.id for a in result] == ["na", "nb", "nc"]
        # only one /assets/batch call regardless of file count
        init_call = mock_http.post.call_args_list[0]
        assert init_call[0][0] == "/api/v1/assets/batch"
        assert len(init_call[1]["json"]["assets"]) == 3
        # 3 complete calls
        complete_paths = [c[0][0] for c in mock_http.post.call_args_list[1:]]
        assert complete_paths == ["/api/v1/files/upload/complete"] * 3

    def test_empty_batch_returns_empty(self, mock_http: Mock) -> None:
        resource = AssetsResource({"workspace-uuid-1": mock_http})
        assert (
            resource.upload_batch(
                hub_profile_id=HUB_PROFILE_ID,
                files=[],
                workspace_id="workspace-uuid-1",
            )
            == []
        )
        mock_http.post.assert_not_called()

    @respx.mock
    def test_batch_size_mismatch_raises(self, mock_http: Mock, text_file: Path) -> None:
        # backend returns 2 inits for 1 input
        mock_http.post.side_effect = [
            [
                {"id": "1", "uploadId": "1", "urls": ["x"], "$type": "File"},
                {"id": "2", "uploadId": "2", "urls": ["y"], "$type": "File"},
            ],
        ]
        resource = AssetsResource({"workspace-uuid-1": mock_http})
        with pytest.raises(RuntimeError, match="2 init records for 1 files"):
            resource.upload_batch(
                hub_profile_id=HUB_PROFILE_ID,
                files=[AssetUploadInput(file=text_file)],
                workspace_id="workspace-uuid-1",
            )


class TestAsyncUpload:
    @respx.mock
    async def test_async_upload_text_file(
        self, async_mock_http: AsyncMock, text_file: Path
    ) -> None:
        urls = ["https://s3.example/async-txt"]
        respx.put(urls[0]).mock(
            return_value=httpx.Response(200, headers={"ETag": '"a"'})
        )
        async_mock_http.post.side_effect = [
            [{"id": "an", "uploadId": "au", "urls": urls, "$type": "File"}],
            None,  # complete
        ]
        async_mock_http.get.return_value = {
            "$type": "File",
            "id": "an",
            "name": "notes.txt",
            "extension": "txt",
            "memorySizeInBytes": text_file.stat().st_size,
            "fileType": "text/plain",
            "url": "https://cdn/n",
            "readOnly": False,
        }

        resource = AsyncAssetsResource({"workspace-uuid-1": async_mock_http})
        asset = await resource.upload(
            hub_profile_id=HUB_PROFILE_ID,
            file=text_file,
            workspace_id="workspace-uuid-1",
        )

        assert asset.id == "an"
        complete_call = async_mock_http.post.call_args_list[1]
        assert complete_call[0][0] == "/api/v1/files/upload/complete"


class TestDeprecatedCreate:
    def test_create_emits_deprecation_warning(self, mock_http: Mock) -> None:
        mock_http.post.return_value = MEDIA_ASSET_PAYLOAD
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            resource.create(
                hub_profile_id=HUB_PROFILE_ID,
                asset=EmbedAssetCreate(name="e", url="https://x"),
                workspace_id="workspace-uuid-1",
            )

        msgs = [
            str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert any("create is deprecated" in m for m in msgs)

    def test_create_batch_emits_deprecation_warning(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = AssetsResource({"workspace-uuid-1": mock_http})

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            resource.create_batch(
                hub_profile_id=HUB_PROFILE_ID,
                assets=[],
                workspace_id="workspace-uuid-1",
            )

        msgs = [
            str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert any("create_batch is deprecated" in m for m in msgs)

    async def test_async_create_emits_deprecation_warning(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.post.return_value = MEDIA_ASSET_PAYLOAD
        resource = AsyncAssetsResource({"workspace-uuid-1": async_mock_http})

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            await resource.create(
                hub_profile_id=HUB_PROFILE_ID,
                asset=EmbedAssetCreate(name="e", url="https://x"),
                workspace_id="workspace-uuid-1",
            )

        msgs = [
            str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert any("create is deprecated" in m for m in msgs)


class TestDollarTypeBackcompat:
    """Legacy ``dollar_type=`` kwarg still works but warns."""

    def test_dollar_type_kwarg_still_accepted(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            m = MediaAssetCreate(dollar_type="Media", name="x")

        assert m.type == "Media"
        msgs = [
            str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        assert any("dollar_type" in m for m in msgs)

    def test_default_type_serializes_with_dollar_alias(self) -> None:
        m = ImageAssetCreate(
            name="x", extension="png", width=1, height=1, memory_size_in_bytes=1
        )
        dumped = m.model_dump(by_alias=True, exclude_none=True)
        assert dumped["$type"] == "Image"
        assert "dollarType" not in dumped
        assert "type" not in dumped
