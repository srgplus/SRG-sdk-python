from unittest.mock import AsyncMock, Mock

from srg.resources.contents import AsyncContentsResource, ContentsResource
from srg.schemas.content import ContentChannelUpsert

CONTENT_ID = "content-uuid-1"
HUB_PROFILE_ID = "hub-profile-uuid-1"

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
        resource = ContentsResource(mock_http)

        result = resource.create(name="My Content", hub_profile_id=HUB_PROFILE_ID)

        mock_http.post.assert_called_once()
        path, kwargs = mock_http.post.call_args[0][0], mock_http.post.call_args[1]
        assert path == "/api/v1/contents"
        assert kwargs["json"]["name"] == "My Content"
        assert kwargs["json"]["hubProfileId"] == HUB_PROFILE_ID
        assert kwargs["json"]["privacy"] == "Preview"
        assert result.id == CONTENT_ID

    def test_post_with_channels(self, mock_http: Mock) -> None:
        mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = ContentsResource(mock_http)

        resource.create(
            name="X",
            hub_profile_id=HUB_PROFILE_ID,
            channels=[ContentChannelUpsert(channel_id="ch-1", category_ids=["cat-1"])],
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["channels"] == [{"channelId": "ch-1", "categoryIds": ["cat-1"]}]

    def test_privacy_default_is_preview(self, mock_http: Mock) -> None:
        mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = ContentsResource(mock_http)
        resource.create(name="X", hub_profile_id=HUB_PROFILE_ID)
        assert mock_http.post.call_args[1]["json"]["privacy"] == "Preview"


class TestContentsGet:
    def test_get_without_hub_profile_id(
        self, mock_http: Mock, content_payload: dict
    ) -> None:
        mock_http.get.return_value = content_payload
        resource = ContentsResource(mock_http)

        result = resource.get(CONTENT_ID)

        mock_http.get.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}", params=None
        )
        assert result.id == CONTENT_ID
        assert result.name == "My Content"

    def test_get_with_hub_profile_id(
        self, mock_http: Mock, content_payload: dict
    ) -> None:
        mock_http.get.return_value = content_payload
        resource = ContentsResource(mock_http)

        resource.get(CONTENT_ID, hub_profile_id=HUB_PROFILE_ID)

        mock_http.get.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}",
            params={"hubProfileId": HUB_PROFILE_ID},
        )


class TestContentsFilter:
    def test_filter_builds_correct_body(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = ContentsResource(mock_http)

        result = resource.filter(HUB_PROFILE_ID, page_size=20)

        body = mock_http.post.call_args[1]["json"]
        assert body["pageSize"] == 20
        assert body["onlyArchived"] is False
        assert body["type"] == ["Content", "Collection"]
        assert result.items == []
        assert result.cursor is None

    def test_filter_with_cursor(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"items": [], "cursor": None}
        resource = ContentsResource(mock_http)

        resource.filter(HUB_PROFILE_ID, page_size=10, cursor="abc")

        assert mock_http.post.call_args[1]["json"]["cursor"] == "abc"


class TestContentsSections:
    def test_create_section_typed_params(self, mock_http: Mock) -> None:
        mock_http.post.return_value = None
        resource = ContentsResource(mock_http)

        resource.create_section(CONTENT_ID, "assets", name="Intro")

        mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections",
            json={"name": "Intro"},
        )

    def test_update_section_typed_params(self, mock_http: Mock) -> None:
        mock_http.put.return_value = None
        resource = ContentsResource(mock_http)

        resource.update_section(CONTENT_ID, "assets", "section-1", name="Updated")

        mock_http.put.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections/section-1",
            json={"name": "Updated"},
        )


class TestContentsProgression:
    def test_patch_content_progression(self, mock_http: Mock) -> None:
        mock_http.patch.return_value = {"status": "Completed"}
        resource = ContentsResource(mock_http)

        result = resource.patch_content_progression(CONTENT_ID, status="Completed")

        mock_http.patch.assert_called_once_with(
            f"/api/v1/progressions/contents/{CONTENT_ID}",
            json={"status": "Completed"},
        )
        assert result.status == "Completed"

    def test_patch_content_progression_returns_empty_on_none(
        self, mock_http: Mock
    ) -> None:
        mock_http.patch.return_value = None
        resource = ContentsResource(mock_http)

        result = resource.patch_content_progression(CONTENT_ID, status="Completed")

        assert result.status is None


class TestContentsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [{"id": str(i), "name": n} for i, n in enumerate(names)]
        return {"items": items, "cursor": cursor}

    def test_single_page_yields_all_items(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page(["A", "B"], cursor=None)
        resource = ContentsResource(mock_http)

        result = list(resource.filter_all(HUB_PROFILE_ID))

        assert [r.name for r in result] == ["A", "B"]
        assert mock_http.post.call_count == 1

    def test_multiple_pages_yields_all_items(self, mock_http: Mock) -> None:
        pages = [
            self._page(["A", "B"], cursor="cur2"),
            self._page(["C"], cursor=None),
        ]
        mock_http.post.side_effect = pages
        resource = ContentsResource(mock_http)

        result = list(resource.filter_all(HUB_PROFILE_ID))

        assert [r.name for r in result] == ["A", "B", "C"]
        assert mock_http.post.call_count == 2

    def test_cursor_passed_to_second_call(self, mock_http: Mock) -> None:
        pages = [
            self._page(["A"], cursor="next"),
            self._page(["B"], cursor=None),
        ]
        mock_http.post.side_effect = pages
        resource = ContentsResource(mock_http)

        list(resource.filter_all(HUB_PROFILE_ID))

        first_body = mock_http.post.call_args_list[0][1]["json"]
        second_body = mock_http.post.call_args_list[1][1]["json"]
        assert "cursor" not in first_body
        assert second_body["cursor"] == "next"

    def test_empty_result(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource(mock_http)

        assert list(resource.filter_all(HUB_PROFILE_ID)) == []

    def test_default_page_size_is_50(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource(mock_http)

        list(resource.filter_all(HUB_PROFILE_ID))

        assert mock_http.post.call_args[1]["json"]["pageSize"] == 50

    def test_custom_page_size(self, mock_http: Mock) -> None:
        mock_http.post.return_value = self._page([], cursor=None)
        resource = ContentsResource(mock_http)

        list(resource.filter_all(HUB_PROFILE_ID, page_size=10))

        assert mock_http.post.call_args[1]["json"]["pageSize"] == 10


class TestContentsSearchAll:
    def test_yields_all_search_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = [
            {"id": "1", "name": "Intro"},
            {"id": "2", "name": "Intro Advanced"},
        ]
        resource = ContentsResource(mock_http)

        result = list(resource.search_all(HUB_PROFILE_ID, search="intro"))

        assert [r.name for r in result] == ["Intro", "Intro Advanced"]
        assert mock_http.post.call_count == 1

    def test_empty_search_results(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = ContentsResource(mock_http)

        assert list(resource.search_all(HUB_PROFILE_ID, search="nothing")) == []


UPLOAD_SIGNED_URL_NO_COVER = {
    "id": CONTENT_ID,
    "coverSignedUrl": None,
    "coverExtension": None,
    "context": [],
    "metadataHeaders": None,
}


class TestContentsUpdateMerge:
    """
    update() must do GET v2 first and merge: fields passed as None keep their
    existing values; only explicitly provided values are replaced.
    """

    def test_get_v2_is_called_before_put(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        mock_http.get.assert_called_once_with(f"/api/v2/contents/{CONTENT_ID}")
        mock_http.put.assert_called_once()

    def test_preserves_name_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        body = mock_http.put.call_args[1]["json"]
        assert body["name"] == "My Content"

    def test_replaces_name_when_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID, name="New Name")

        assert mock_http.put.call_args[1]["json"]["name"] == "New Name"

    def test_preserves_privacy_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        # existing fixture has privacy="Public" — must not be reset to "Preview"
        assert mock_http.put.call_args[1]["json"]["privacy"] == "Public"

    def test_replaces_privacy_when_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID, privacy="Private")

        assert mock_http.put.call_args[1]["json"]["privacy"] == "Private"

    def test_preserves_channels_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        body = mock_http.put.call_args[1]["json"]
        # Existing channel has two categories; must be serialised as upsert format.
        assert body["channels"] == [
            {"channelId": "channel-uuid-1", "categoryIds": ["cat-1", "cat-2"]}
        ]

    def test_clears_channels_when_empty_list_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID, channels=[])

        assert mock_http.put.call_args[1]["json"]["channels"] == []

    def test_replaces_channels_when_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID, channels=["ch-new"])

        assert mock_http.put.call_args[1]["json"]["channels"] == [
            {"channelId": "ch-new", "categoryIds": []}
        ]

    def test_preserves_context_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        body = mock_http.put.call_args[1]["json"]
        assert len(body["context"]) == 2
        assert body["context"][0]["$type"] == "Text"

    def test_replaces_context_when_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        new_context = [{"$type": "Text", "content": "Updated"}]
        resource.update(CONTENT_ID, context=new_context)

        assert mock_http.put.call_args[1]["json"]["context"] == new_context

    def test_preserves_categories_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        body = mock_http.put.call_args[1]["json"]
        assert body["categories"] == [{"id": "cat-1"}, {"id": "cat-2"}]

    def test_preserves_details_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        assert mock_http.put.call_args[1]["json"]["details"] == "Existing details"

    def test_preserves_main_asset_when_not_provided(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        assert mock_http.put.call_args[1]["json"]["mainAssetId"] == "asset-1"

    def test_put_called_on_correct_endpoint(
        self, mock_http: Mock, content_v2_payload: dict
    ) -> None:
        mock_http.get.return_value = content_v2_payload
        mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = ContentsResource(mock_http)

        resource.update(CONTENT_ID)

        assert mock_http.put.call_args[0][0] == f"/api/v1/contents/{CONTENT_ID}"


class TestAsyncContentsUpdateMerge:
    """Async mirror of TestContentsUpdateMerge."""

    async def test_get_v2_is_called_before_put(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource(async_mock_http)

        await resource.update(CONTENT_ID)

        async_mock_http.get.assert_called_once_with(f"/api/v2/contents/{CONTENT_ID}")
        async_mock_http.put.assert_called_once()

    async def test_preserves_privacy_when_not_provided(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource(async_mock_http)

        await resource.update(CONTENT_ID)

        assert async_mock_http.put.call_args[1]["json"]["privacy"] == "Public"

    async def test_preserves_channels_when_not_provided(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource(async_mock_http)

        await resource.update(CONTENT_ID)

        body = async_mock_http.put.call_args[1]["json"]
        assert body["channels"] == [
            {"channelId": "channel-uuid-1", "categoryIds": ["cat-1", "cat-2"]}
        ]

    async def test_replaces_context_when_provided(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource(async_mock_http)

        new_context = [{"$type": "Text", "content": "New"}]
        await resource.update(CONTENT_ID, context=new_context)

        assert async_mock_http.put.call_args[1]["json"]["context"] == new_context

    async def test_clears_channels_when_empty_list_provided(
        self, async_mock_http: AsyncMock, content_v2_payload: dict
    ) -> None:
        async_mock_http.get.return_value = content_v2_payload
        async_mock_http.put.return_value = UPLOAD_SIGNED_URL_NO_COVER
        resource = AsyncContentsResource(async_mock_http)

        await resource.update(CONTENT_ID, channels=[])

        assert async_mock_http.put.call_args[1]["json"]["channels"] == []


class TestAsyncContentsCreate:
    async def test_post_with_required_fields(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = UPLOAD_SIGNED_URL_PAYLOAD
        resource = AsyncContentsResource(async_mock_http)

        result = await resource.create(name="My Content", hub_profile_id=HUB_PROFILE_ID)

        async_mock_http.post.assert_called_once()
        assert result.id == CONTENT_ID

    async def test_create_section_typed_params(
        self, async_mock_http: AsyncMock
    ) -> None:
        async_mock_http.post.return_value = None
        resource = AsyncContentsResource(async_mock_http)

        await resource.create_section(CONTENT_ID, "assets", name="Intro")

        async_mock_http.post.assert_called_once_with(
            f"/api/v1/contents/{CONTENT_ID}/assets/sections",
            json={"name": "Intro"},
        )


class TestAsyncContentsFilterAll:
    def _page(self, names: list[str], cursor: str | None) -> dict:
        items = [{"id": str(i), "name": n} for i, n in enumerate(names)]
        return {"items": items, "cursor": cursor}

    async def test_single_page(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = self._page(["A", "B"], cursor=None)
        resource = AsyncContentsResource(async_mock_http)

        result = [item async for item in resource.filter_all(HUB_PROFILE_ID)]

        assert [r.name for r in result] == ["A", "B"]

    async def test_multiple_pages(self, async_mock_http: AsyncMock) -> None:
        pages = [
            self._page(["A", "B"], cursor="cur2"),
            self._page(["C"], cursor=None),
        ]
        async_mock_http.post.side_effect = pages
        resource = AsyncContentsResource(async_mock_http)

        result = [item async for item in resource.filter_all(HUB_PROFILE_ID)]

        assert [r.name for r in result] == ["A", "B", "C"]
        assert async_mock_http.post.call_count == 2

    async def test_search_all(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = [
            {"id": "1", "name": "Intro"},
            {"id": "2", "name": "Intro Advanced"},
        ]
        resource = AsyncContentsResource(async_mock_http)

        result = [
            item async for item in resource.search_all(HUB_PROFILE_ID, search="intro")
        ]

        assert [r.name for r in result] == ["Intro", "Intro Advanced"]
