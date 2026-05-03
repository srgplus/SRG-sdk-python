from unittest.mock import AsyncMock, Mock

from srg.resources.channels import AsyncChannelsResource, ChannelsResource
from srg.schemas.channel import CategoryToReorder

CHANNEL_ID = "channel-uuid-1"
HUB_PROFILE_ID = "hub-profile-uuid-1"


class TestChannelsCreate:
    def test_create_returns_id(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"id": CHANNEL_ID}
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = resource.create(
            name="My Channel",
            hub_profile_id=HUB_PROFILE_ID,
            privacy="Public",
            workspace_id="workspace-uuid-1",
        )

        mock_http.post.assert_called_once_with(
            "/api/v1/channels",
            json={
                "name": "My Channel",
                "hubProfileId": HUB_PROFILE_ID,
                "privacy": "Public",
            },
        )
        assert result == CHANNEL_ID

    def test_create_default_privacy_is_private(self, mock_http: Mock) -> None:
        mock_http.post.return_value = {"id": CHANNEL_ID}
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        resource.create(
            name="X", hub_profile_id=HUB_PROFILE_ID, workspace_id="workspace-uuid-1"
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["privacy"] == "Private"


class TestChannelsUpdate:
    def test_update_sends_correct_body(self, mock_http: Mock) -> None:
        mock_http.put.return_value = None
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        resource.update(
            channel_id=CHANNEL_ID,
            hub_profile_id=HUB_PROFILE_ID,
            name="Renamed",
            privacy="Public",
            workspace_id="workspace-uuid-1",
        )

        body = mock_http.put.call_args[1]["json"]
        assert body["channelId"] == CHANNEL_ID
        assert body["name"] == "Renamed"
        assert body["privacy"] == "Public"

    def test_update_with_categories(self, mock_http: Mock) -> None:
        mock_http.put.return_value = None
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        resource.update(
            channel_id=CHANNEL_ID,
            hub_profile_id=HUB_PROFILE_ID,
            name="X",
            categories=[CategoryToReorder(id="cat-1", order=0)],
            workspace_id="workspace-uuid-1",
        )

        body = mock_http.put.call_args[1]["json"]
        assert body["categories"] == [{"id": "cat-1", "order": 0}]


class TestChannelsList:
    def test_list_returns_channels(
        self, mock_http: Mock, channel_payload: dict
    ) -> None:
        mock_http.get.return_value = [channel_payload]
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = resource.list(HUB_PROFILE_ID, workspace_id="workspace-uuid-1")

        call_args = mock_http.get.call_args
        assert call_args[0][0] == f"/api/v1/channels/{HUB_PROFILE_ID}"
        assert len(result) == 1
        assert result[0].id == CHANNEL_ID
        assert result[0].name == "Main Channel"

    def test_get_returns_hub_profile_channel_v2(
        self, mock_http: Mock, channel_payload: dict
    ) -> None:
        mock_http.get.return_value = channel_payload
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = resource.get(CHANNEL_ID, workspace_id="workspace-uuid-1")

        mock_http.get.assert_called_once_with(f"/api/v2/channels/{CHANNEL_ID}")
        assert result.id == CHANNEL_ID
        assert result.name == "Main Channel"
        assert result.privacy == "Public"
        assert result.hub_profile_name == "Test Profile"


class TestChannelsGetCategory:
    def test_get_category_references_paged(self, mock_http: Mock) -> None:
        mock_http.get.return_value = {"items": [], "cursor": None}
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = resource.get_category_references(
            CHANNEL_ID, "cat-1", page_size=10, workspace_id="workspace-uuid-1"
        )

        params = mock_http.get.call_args[1]["params"]
        assert params["pageSize"] == 10
        assert result.cursor is None


class TestChannelsGetCategoryReferencesAll:
    def _page(self, count: int, cursor: str | None) -> dict:
        items = [
            {"contentId": f"c-{i}", "order": i, "sectionId": None} for i in range(count)
        ]
        return {"items": items, "cursor": cursor}

    def test_single_page_yields_all(self, mock_http: Mock) -> None:
        mock_http.get.return_value = self._page(3, cursor=None)
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.get_category_references_all(
                CHANNEL_ID, "cat-1", workspace_id="workspace-uuid-1"
            )
        )

        assert len(result) == 3
        assert mock_http.get.call_count == 1

    def test_multiple_pages(self, mock_http: Mock) -> None:
        pages = [
            self._page(2, cursor="cur2"),
            self._page(1, cursor=None),
        ]
        mock_http.get.side_effect = pages
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        result = list(
            resource.get_category_references_all(
                CHANNEL_ID, "cat-1", workspace_id="workspace-uuid-1"
            )
        )

        assert len(result) == 3
        assert mock_http.get.call_count == 2

    def test_cursor_passed_to_second_call(self, mock_http: Mock) -> None:
        pages = [
            self._page(1, cursor="next"),
            self._page(1, cursor=None),
        ]
        mock_http.get.side_effect = pages
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        list(
            resource.get_category_references_all(
                CHANNEL_ID, "cat-1", workspace_id="workspace-uuid-1"
            )
        )

        second_params = mock_http.get.call_args_list[1][1]["params"]
        assert second_params["cursor"] == "next"

    def test_default_page_size_is_50(self, mock_http: Mock) -> None:
        mock_http.get.return_value = self._page(0, cursor=None)
        resource = ChannelsResource({"workspace-uuid-1": mock_http})

        list(
            resource.get_category_references_all(
                CHANNEL_ID, "cat-1", workspace_id="workspace-uuid-1"
            )
        )

        assert mock_http.get.call_args[1]["params"]["pageSize"] == 50


class TestAsyncChannels:
    async def test_create_returns_id(self, async_mock_http: AsyncMock) -> None:
        async_mock_http.post.return_value = {"id": CHANNEL_ID}
        resource = AsyncChannelsResource({"workspace-uuid-1": async_mock_http})

        result = await resource.create(
            name="My Channel",
            hub_profile_id=HUB_PROFILE_ID,
            workspace_id="workspace-uuid-1",
        )

        assert result == CHANNEL_ID

    async def test_get_category_references_all(
        self, async_mock_http: AsyncMock
    ) -> None:
        def _page(count: int, cursor: str | None) -> dict:
            items = [
                {"contentId": f"c-{i}", "order": i, "sectionId": None}
                for i in range(count)
            ]
            return {"items": items, "cursor": cursor}

        pages = [_page(2, cursor="cur2"), _page(1, cursor=None)]
        async_mock_http.get.side_effect = pages
        resource = AsyncChannelsResource({"workspace-uuid-1": async_mock_http})

        result = [
            item
            async for item in resource.get_category_references_all(
                CHANNEL_ID, "cat-1", workspace_id="workspace-uuid-1"
            )
        ]

        assert len(result) == 3
        assert async_mock_http.get.call_count == 2
