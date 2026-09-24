import struct
from unittest.mock import AsyncMock, Mock

import pytest

from srg.exceptions import SRGError
from srg.resources.contents import AsyncContentsResource, ContentsResource
from srg.schemas.common import ContentFileUploadParameters
from srg.schemas.content import ContentChannelUpsert

CONTENT_ID = "content-uuid-1"
HUB_PROFILE_ID = "hub-profile-uuid-1"

# Minimal PNG: signature + IHDR declaring 1080x1920 (enough for type/size sniffing).
PNG_1080x1920 = (
    b"\x89PNG\r\n\x1a\n"
    + b"\x00\x00\x00\x0dIHDR"
    + struct.pack(">II", 1080, 1920)
    + b"\x08\x02\x00\x00\x00"
    + b"\x00" * 16
)

UPLOAD_SIGNED_URL_PAYLOAD = {
    "id": CONTENT_ID,
    "coverSignedUrl": None,
    "coverExtension": None,
    "context": [],
    "metadataHeaders": None,
}


class TestContentsCreate:
    def test_post_with_required_fields(self, mock_http: Mock) -> None:
        mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.create(
            name="My Content",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        mock_http.post.assert_called_once()
        path, kwargs = mock_http.post.call_args[0][0], mock_http.post.call_args[1]
        assert path == "/api/v1/contents"
        assert kwargs["json"]["name"] == "My Content"
        assert kwargs["json"]["hubProfileId"] == HUB_PROFILE_ID
        assert kwargs["json"]["privacy"] == "Preview"
        assert result.id == CONTENT_ID

    def test_post_with_channels(self, mock_http: Mock) -> None:
        mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.create(
            name="X",
            hub_profile_id=HUB_PROFILE_ID,
            channels=[ContentChannelUpsert(channel_id="ch-1", category_ids=["cat-1"])],
            workspace_id="workspace-uuid-1",
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["channels"] == [{"channelId": "ch-1", "categoryIds": ["cat-1"]}]

    def test_privacy_default_is_preview(self, mock_http: Mock) -> None:
        mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = ContentsResource({"workspace-uuid-1": mock_http})
        resource.create(
            name="X", hub_profile_id=HUB_PROFILE_ID, workspace_id="workspace-uuid-1"
        )
        assert mock_http.post.call_args[1]["json"]["privacy"] == "Preview"


class TestContentsGet:
    def test_get_without_hub_profile_id(
        self, mock_http: Mock, content_payload: dict
    ) -> None:
        mock_http.get.return_value = content_payload
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.get(CONTENT_ID, workspace_id="workspace-uuid-1")

        mock_http.get.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}", params=None
        )
        assert result.id == CONTENT_ID
        assert result.name == "My Content"

    def test_get_with_hub_profile_id(
        self, mock_http: Mock, content_payload: dict
    ) -> None:
        mock_http.get.return_value = content_payload
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.get(
            CONTENT_ID, hub_profile_id=HUB_PROFILE_ID, workspace_id="workspace-uuid-1"
        )

        mock_http.get.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}",
            params={"hubProfileId": HUB_PROFILE_ID},
        )


class TestContentsFilter:
    def test_filter_builds_correct_body(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.filter(
            HUB_PROFILE_ID, page_size=20, workspace_id="workspace-uuid-1"
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["pageSize"] == 20
        assert body["onlyArchived"] is False
        assert body["type"] == ["Content", "Collection"]
        assert result.items == []
        assert result.cursor is None

    def test_filter_with_cursor(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.filter(
            HUB_PROFILE_ID, page_size=10, cursor="abc", workspace_id="workspace-uuid-1"
        )

        assert mock_http.post.call_args[1]["json"]["cursor"] == "abc"


class TestContentsSections:
    def test_create_section_typed_params(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"id": "section-uuid-1"}
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.create_section(
            CONTENT_ID, "assets", name="Intro", workspace_id="workspace-uuid-1"
        )

        mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections",
            json={"name": "Intro"},
        )
        assert result.id == "section-uuid-1"

    def test_update_section_typed_params(self, mock_http: Mock) -> None:
        mock_http.put.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.update_section(
            CONTENT_ID,
            "assets",
            "section-1",
            name="Updated",
            workspace_id="workspace-uuid-1",
        )

        mock_http.put.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections/section-1",
            json={"name": "Updated"},
        )


class TestContentsProgression:
    def test_patch_content_progression(self, mock_http: Mock) -> None:
        mock_http.patch.return_value = {"status": "Completed"}
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.patch_content_progression(
            CONTENT_ID, status="Completed", workspace_id="workspace-uuid-1"
        )

        mock_http.patch.assert_called_once_with(
            f"/api/v1/progressions/contents/{CONTENT_ID}",
            json={"status": "Completed"},
        )
        assert result.status == "Completed"

    def test_patch_content_progression_returns_empty_on_none(
        self, mock_http: Mock
    ) -> None:
        mock_http.patch.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = resource.patch_content_progression(
            CONTENT_ID, status="Completed", workspace_id="workspace-uuid-1"
        )

        assert result.status is None


class TestContentsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [{"id": str(i), "name": n} for i, n in enumerate(names)]
        return {"items": items, "cursor": cursor}

    def test_single_page_yields_all_items(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page(["A", "B"], cursor=None)
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1")
        )

        assert [r.name for r in result] == ["A", "B"]
        assert mock_http.post.call_count == 1

    def test_multiple_pages_yields_all_items(self, mock_http: Mock) -> None:
        pages = [
            self._page(["A", "B"], cursor="cur2"),
            self._page(["C"], cursor=None),
        ]
        mock_http.post.side_effect = pages
        resource = ContentsResource({"workspace-uuid-1": mock_http})

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
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))

        first_body = mock_http.post.call_args_list[0][1]["json"]
        second_body = mock_http.post.call_args_list[1][1]["json"]
        assert "cursor" not in first_body
        assert second_body["cursor"] == "next"

    def test_empty_result(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        assert (
            list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))
            == []
        )

    def test_default_page_size_is_50(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        list(resource.filter_all(HUB_PROFILE_ID, workspace_id="workspace-uuid-1"))

        assert mock_http.post.call_args[1]["json"]["pageSize"] == 50

    def test_custom_page_size(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        list(
            resource.filter_all(
                HUB_PROFILE_ID, page_size=10, workspace_id="workspace-uuid-1"
            )
        )

        assert mock_http.post.call_args[1]["json"]["pageSize"] == 10


class TestContentsSearchAll:
    def test_yields_all_search_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = [
            {"id": "1", "name": "Intro"},
            {"id": "2", "name": "Intro Advanced"},
        ]
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.search_all(
                HUB_PROFILE_ID, search="intro", workspace_id="workspace-uuid-1"
            )
        )

        assert [r.name for r in result] == ["Intro", "Intro Advanced"]
        assert mock_http.post.call_count == 1

    def test_empty_search_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        assert (
            list(
                resource.search_all(
                    HUB_PROFILE_ID, search="nothing", workspace_id="workspace-uuid-1"
                )
            )
            == []
        )


UPLOAD_SIGNED_URL_NO_COVER = {
    "id": CONTENT_ID,
    "coverSignedUrl": None,
    "coverExtension": None,
    "context": [],
    "metadataHeaders": None,
}


class TestContentsUpdatePatch:
    """
    update() sends PATCH with ONLY the supplied fields. The backend keeps every
    omitted field (cover, main asset, channels, categories, action buttons), so
    an update that doesn't mention the cover can never wipe it (SRGDEV-235:
    the old GET-merge-PUT omitted `cover`, and PUT treats that as "remove").
    """

    @staticmethod
    def _resource(mock_http: Mock) -> ContentsResource:
        mock_http.patch.return_value = UPLOAD_SIGNED_URL_NO_COVER
        return ContentsResource({"workspace-uuid-1": mock_http})

    def test_uses_patch_on_content_endpoint(self, mock_http: Mock) -> None:
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            name="New Name",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        mock_http.put.assert_not_called()
        mock_http.patch.assert_called_once()
        assert mock_http.patch.call_args[0][0] == f"/api/v1/contents/{CONTENT_ID}"
        assert mock_http.patch.call_args[1]["params"] == {
            "hubProfileId": HUB_PROFILE_ID
        }

    def test_context_only_update_never_touches_cover(self, mock_http: Mock) -> None:
        """Regression: rewriting the body must not send (and so not wipe) the cover."""
        resource = self._resource(mock_http)
        new_context = [{"$type": "Text", "content": "caption"}]

        resource.update(
            CONTENT_ID,
            context=new_context,
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        body = mock_http.patch.call_args[1]["json"]
        assert body == {"context": new_context}
        assert "cover" not in body
        assert "mainAssetId" not in body
        assert "channels" not in body
        assert "categories" not in body

    def test_only_supplied_scalars_are_sent(self, mock_http: Mock) -> None:
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            privacy="Private",
            details="New details",
            url="https://example.org",
            main_asset_id="asset-2",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert mock_http.patch.call_args[1]["json"] == {
            "privacy": "Private",
            "details": "New details",
            "url": "https://example.org",
            "mainAssetId": "asset-2",
        }

    def test_resolves_hub_profile_from_content_when_missing(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        resource = self._resource(mock_http)

        resource.update(CONTENT_ID, name="N", workspace_id="workspace-uuid-1")

        mock_http.get.assert_called_once_with(f"/api/v2/contents/{CONTENT_ID}")
        assert mock_http.patch.call_args[1]["params"] == {
            "hubProfileId": HUB_PROFILE_ID
        }
        # The read is only for the hub id — nothing from it is written back.
        assert mock_http.patch.call_args[1]["json"] == {"name": "N"}

    def test_no_read_when_hub_profile_is_passed(self, mock_http: Mock) -> None:
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            name="N",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        mock_http.get.assert_not_called()

    def test_clears_channels_when_empty_list_provided(self, mock_http: Mock) -> None:
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            channels=[],
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert mock_http.patch.call_args[1]["json"] == {"channels": []}

    def test_replaces_channels_when_provided(self, mock_http: Mock) -> None:
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            channels=["ch-new"],
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert mock_http.patch.call_args[1]["json"]["channels"] == [
            {"channelId": "ch-new", "categoryIds": []}
        ]

    def test_manual_keep_cover_marker_keeps_image_key(self, mock_http: Mock) -> None:
        """The backend DTO requires `image` to be present, even when null."""
        resource = self._resource(mock_http)

        resource.update(
            CONTENT_ID,
            cover=ContentFileUploadParameters(image=None, generate_signed_url=False),
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert mock_http.patch.call_args[1]["json"]["cover"] == {
            "image": None,
            "generateSignedUrl": False,
        }


class TestContentsUpdateCoverImage:
    """cover_image: type + dimensions come from the bytes, so URLs need no extension."""

    SIGNED = {
        "id": CONTENT_ID,
        "coverSignedUrl": {"url": "https://r2.example/signed-put"},
        "coverExtension": "png",
        "context": [],
        "metadataHeaders": {"x-amz-meta-type": "ContentCover"},
    }

    def test_extensionless_url_uses_sniffed_type_and_real_size(
        self, mock_http: Mock, content_payload: dict, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        uploads: list[tuple] = []
        monkeypatch.setattr(
            "srg.resources.contents.read_image_sync",
            lambda _src: (PNG_1080x1920, "binary/octet-stream"),
        )
        monkeypatch.setattr(
            "srg.resources.contents.put_bytes_to_signed_url",
            lambda url, content, ctype, extra_headers=None: uploads.append(
                (url, ctype, extra_headers, len(content))
            ),
        )
        mock_http.patch.return_value = self.SIGNED
        mock_http.get.return_value = content_payload
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.update(
            CONTENT_ID,
            cover_image="https://r2.example/hub-profiles/h/assets/a1?X-Amz-Signature=s",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        cover = mock_http.patch.call_args[1]["json"]["cover"]
        assert cover["generateSignedUrl"] is True
        assert cover["image"] == {
            "width": 1080,
            "height": 1920,
            "size": len(PNG_1080x1920),
            "extension": "png",
        }
        # The PUT carries the MIME the signed URL was bound to, not the
        # server's generic content type, plus the metadata headers.
        assert uploads == [
            (
                "https://r2.example/signed-put",
                "image/png",
                {"x-amz-meta-type": "ContentCover"},
                len(PNG_1080x1920),
            )
        ]

    def test_unrecognised_bytes_without_hints_raise(
        self, mock_http: Mock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "srg.resources.contents.read_image_sync",
            lambda _src: (b"not an image at all", "application/octet-stream"),
        )
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        with pytest.raises(SRGError, match="image type"):
            resource.update(
                CONTENT_ID,
                cover_image="https://example.com/blob",
                hub_profile_id=HUB_PROFILE_ID,
                workspace_id="workspace-uuid-1",
            )
        mock_http.patch.assert_not_called()


class TestContentsSetCoverFromAsset:
    def test_posts_cover_asset_id(self, mock_http: Mock) -> None:
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.set_cover_from_asset(
            CONTENT_ID,
            "asset-9",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/cover/from-asset",
            json={"coverAssetId": "asset-9"},
            params={"hubProfileId": HUB_PROFILE_ID},
        )

    def test_resolves_hub_profile_when_missing(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.set_cover_from_asset(
            CONTENT_ID, "asset-9", workspace_id="workspace-uuid-1"
        )

        assert mock_http.post.call_args[1]["params"] == {"hubProfileId": HUB_PROFILE_ID}


class TestAsyncContentsUpdatePatch:
    """Async mirror of TestContentsUpdatePatch."""

    async def test_context_only_update_never_touches_cover(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.patch.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})
        new_context = [{"$type": "Text", "content": "New"}]

        await resource.update(
            CONTENT_ID,
            context=new_context,
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        async_mock_http.put.assert_not_called()
        assert async_mock_http.patch.call_args[0][0] == f"/api/v1/contents/{CONTENT_ID}"
        assert async_mock_http.patch.call_args[1]["json"] == {"context": new_context}

    async def test_resolves_hub_profile_from_content_when_missing(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.patch.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.update(
            CONTENT_ID, privacy="Private", workspace_id="workspace-uuid-1"
        )

        async_mock_http.get.assert_called_once_with(f"/api/v2/contents/{CONTENT_ID}")
        assert async_mock_http.patch.call_args[1]["params"] == {
            "hubProfileId": HUB_PROFILE_ID
        }
        assert async_mock_http.patch.call_args[1]["json"] == {"privacy": "Private"}

    async def test_clears_channels_when_empty_list_provided(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.patch.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.update(
            CONTENT_ID,
            channels=[],
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert async_mock_http.patch.call_args[1]["json"] == {"channels": []}

    async def test_set_cover_from_asset(self, async_mock_http: AsyncMock) -> None:
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.set_cover_from_asset(
            CONTENT_ID,
            "asset-9",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        async_mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/cover/from-asset",
            json={"coverAssetId": "asset-9"},
            params={"hubProfileId": HUB_PROFILE_ID},
        )


class TestAsyncContentsCreate:
    async def test_post_with_required_fields(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        result = await resource.create(
            name="My Content",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        async_mock_http.post.assert_called_once()
        assert result.id == CONTENT_ID

    async def test_create_section_typed_params(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.post.return_value = {"id": "section-uuid-1"}
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        result = await resource.create_section(
            CONTENT_ID, "assets", name="Intro", workspace_id="workspace-uuid-1"
        )

        async_mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections",
            json={"name": "Intro"},
        )
        assert result.id == "section-uuid-1"


class TestAsyncContentsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [{"id": str(i), "name": n} for i, n in enumerate(names)]
        return {"items": items, "cursor": cursor}

    async def test_single_page(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = self._page(["A", "B"], cursor=None)
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

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
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

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
            {"id": "1", "name": "Intro"},
            {"id": "2", "name": "Intro Advanced"},
        ]
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        result = [
            item
            async for item in resource.search_all(
                HUB_PROFILE_ID, search="intro", workspace_id="workspace-uuid-1"
            )
        ]

        assert [r.name for r in result] == ["Intro", "Intro Advanced"]


SECTION_ID = "section-uuid-1"
REFERENCE_ID = "ref-uuid-1"
REFERENCE_ID_2 = "ref-uuid-2"
CATEGORY_NAME = "Content"

SUBCONTENT_ITEM_PAYLOAD = {
    "$type": "Content",
    "id": REFERENCE_ID,
    "name": "Child Content",
    "cursor": "cursor-abc",
    "section": {
        "$type": "Section",
        "id": SECTION_ID,
        "cursor": "sec-cursor",
        "name": "Chapter 1",
    },
    "created": "2024-01-01T00:00:00Z",
    "cover": None,
    "privacy": "Public",
    "previewText": None,
    "progression": None,
}


class TestContentsSubcontent:
    def test_add_subcontent(self, mock_http: Mock) -> None:
        mock_http.post.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.add_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            SECTION_ID,
            subcontent_ids=[REFERENCE_ID, REFERENCE_ID_2],
            workspace_id="workspace-uuid-1",
        )

        mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}/{SECTION_ID}/references",
            json={"referenceIds": [REFERENCE_ID, REFERENCE_ID_2]},
        )

    def test_get_subcontent_returns_page(self, mock_http: Mock) -> None:
        mock_http.get.return_value = {
            "items": [SUBCONTENT_ITEM_PAYLOAD],
            "cursor": None,
        }
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        page = resource.get_subcontent(
            CONTENT_ID, CATEGORY_NAME, page_size=10, workspace_id="workspace-uuid-1"
        )

        mock_http.get.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}/references",
            params={"pageSize": 10, "order": "Asc"},
        )
        assert len(page.items) == 1
        item = page.items[0]
        assert item.id == REFERENCE_ID
        assert item.name == "Child Content"
        assert item.section.name == "Chapter 1"
        assert page.cursor is None

    def test_get_subcontent_with_cursor_and_order(self, mock_http: Mock) -> None:
        mock_http.get.return_value = {"items": [], "cursor": "next"}
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.get_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            page_size=5,
            cursor="prev",
            order="Desc",
            workspace_id="workspace-uuid-1",
        )

        params = mock_http.get.call_args[1]["params"]
        assert params["cursor"] == "prev"
        assert params["order"] == "Desc"
        assert params["pageSize"] == 5

    def test_delete_subcontent(self, mock_http: Mock) -> None:
        mock_http.delete.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.delete_subcontent(
            CONTENT_ID, CATEGORY_NAME, SECTION_ID, REFERENCE_ID, "workspace-uuid-1"
        )

        mock_http.delete.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}"
            f"/{SECTION_ID}/references/{REFERENCE_ID}",
        )

    def test_move_subcontent(self, mock_http: Mock) -> None:
        mock_http.post.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.move_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            SECTION_ID,
            subcontent_id=REFERENCE_ID,
            previous_subcontent_id=REFERENCE_ID_2,
            workspace_id="workspace-uuid-1",
        )

        mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}"
            f"/{SECTION_ID}/references/move",
            json={
                "referenceId": REFERENCE_ID,
                "previousReferenceId": REFERENCE_ID_2,
            },
        )

    def test_move_subcontent_to_first_position(self, mock_http: Mock) -> None:
        mock_http.post.return_value = None
        resource = ContentsResource({"workspace-uuid-1": mock_http})

        resource.move_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            SECTION_ID,
            subcontent_id=REFERENCE_ID,
            workspace_id="workspace-uuid-1",
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["previousReferenceId"] is None


class TestAsyncContentsSubcontent:
    async def test_add_subcontent(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = None
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.add_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            SECTION_ID,
            subcontent_ids=[REFERENCE_ID],
            workspace_id="workspace-uuid-1",
        )

        async_mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}/{SECTION_ID}/references",
            json={"referenceIds": [REFERENCE_ID]},
        )

    async def test_get_subcontent_returns_page(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.get.return_value = {
            "items": [SUBCONTENT_ITEM_PAYLOAD],
            "cursor": "next-page",
        }
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        page = await resource.get_subcontent(
            CONTENT_ID, CATEGORY_NAME, page_size=20, workspace_id="workspace-uuid-1"
        )

        assert len(page.items) == 1
        assert page.items[0].id == REFERENCE_ID
        assert page.cursor == "next-page"

    async def test_delete_subcontent(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.delete.return_value = None
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.delete_subcontent(
            CONTENT_ID, CATEGORY_NAME, SECTION_ID, REFERENCE_ID, "workspace-uuid-1"
        )

        async_mock_http.delete.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}"
            f"/{SECTION_ID}/references/{REFERENCE_ID}",
        )

    async def test_move_subcontent(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = None
        resource = AsyncContentsResource({"workspace-uuid-1": async_mock_http})

        await resource.move_subcontent(
            CONTENT_ID,
            CATEGORY_NAME,
            SECTION_ID,
            subcontent_id=REFERENCE_ID,
            previous_subcontent_id=REFERENCE_ID_2,
            workspace_id="workspace-uuid-1",
        )

        async_mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/{CATEGORY_NAME}"
            f"/{SECTION_ID}/references/move",
            json={
                "referenceId": REFERENCE_ID,
                "previousReferenceId": REFERENCE_ID_2,
            },
        )
