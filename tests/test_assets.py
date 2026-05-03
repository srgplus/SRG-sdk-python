from unittest.mock import AsyncMock, Mock

from srg.resources.assets import AssetsResource, AsyncAssetsResource

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
