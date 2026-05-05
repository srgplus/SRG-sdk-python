from unittest.mock import AsyncMock, Mock

from srg.resources.hub_profiles import AsyncHubProfilesResource, HubProfilesResource

HUB_PROFILE_ID = "hub-profile-uuid-1"
WORKSPACE_ID = "workspace-uuid-1"

SIGNED_URLS_PAYLOAD = {
    "id": HUB_PROFILE_ID,
    "avatarSignedUrl": None,
    "coverSignedUrl": None,
    "avatarExtension": None,
    "coverExtension": None,
    "widgets": [],
}


class TestHubProfilesCreate:
    def test_create_sends_required_fields(self, mock_http: Mock) -> None:
        mock_http.post.return_value = SIGNED_URLS_PAYLOAD
        resource = HubProfilesResource({"workspace-uuid-1": mock_http})

        result = resource.create(
            name="My Profile",
            user_name="myprofile",
            availability_level="Public",
            app_clip_on=False,
            workspace_id=WORKSPACE_ID,
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["name"] == "My Profile"
        assert body["userName"] == "myprofile"
        assert body["availabilityLevel"] == 0  # "Public" maps to 0
        assert result.id == HUB_PROFILE_ID

    def test_create_with_workspace_id(self, mock_http: Mock) -> None:
        mock_http.post.return_value = SIGNED_URLS_PAYLOAD
        resource = HubProfilesResource({"workspace-uuid-1": mock_http})

        resource.create(
            name="X",
            user_name="x",
            availability_level="Public",
            app_clip_on=False,
            workspace_id=WORKSPACE_ID,
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["workspaceId"] == WORKSPACE_ID


class TestHubProfilesGet:
    def test_get_returns_full_profile(
        self, mock_http: Mock, hub_profile_payload: dict
    ) -> None:
        mock_http.get.return_value = hub_profile_payload
        resource = HubProfilesResource({"workspace-uuid-1": mock_http})

        result = resource.get(HUB_PROFILE_ID, workspace_id=WORKSPACE_ID)

        mock_http.get.assert_called_once_with(f"/api/v1/hub-profiles/{HUB_PROFILE_ID}")
        assert result.id == HUB_PROFILE_ID
        assert result.sub_name == "Sub"
        assert result.description == "A description"
        assert len(result.buttons) == 1
        assert result.qr_code is not None


class TestHubProfilesFilter:
    def test_filter_sends_ids(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = HubProfilesResource({"workspace-uuid-1": mock_http})

        resource.filter(ids=["id-1", "id-2"], workspace_id=WORKSPACE_ID)

        body = mock_http.post.call_args[1]["json"]
        assert body["ids"] == ["id-1", "id-2"]

    def test_filter_with_availability_level(self, mock_http: Mock) -> None:
        mock_http.post.return_value = []
        resource = HubProfilesResource({"workspace-uuid-1": mock_http})

        resource.filter(
            ids=["id-1"], availability_level="Public", workspace_id=WORKSPACE_ID
        )

        body = mock_http.post.call_args[1]["json"]
        assert body["availabilityLevel"] == 0  # "Public" maps to 0


class TestAsyncHubProfiles:
    async def test_get_returns_profile(
        self, async_mock_http: AsyncMock, hub_profile_payload: dict
    ) -> None:
        async_mock_http.get.return_value = hub_profile_payload
        resource = AsyncHubProfilesResource({"workspace-uuid-1": async_mock_http})

        result = await resource.get(HUB_PROFILE_ID, workspace_id=WORKSPACE_ID)

        assert result.sub_name == "Sub"
        assert result.qr_code is not None
