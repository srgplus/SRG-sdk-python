from srg.schemas.channel import HubProfileChannel
from srg.schemas.content import ContentV2, MainPlayableAsset
from srg.schemas.hub_profile import (
    ActionButtonResponse,
    GetHubProfile,
    HubProfileQrCode,
)
from srg.schemas.permission import WorkspaceUser


class TestGetHubProfile:
    def test_parses_all_new_fields(self, hub_profile_payload: dict) -> None:
        hp = GetHubProfile.model_validate(hub_profile_payload)

        assert hp.id == "hub-profile-uuid-1"
        assert hp.sub_name == "Sub"
        assert hp.description == "A description"
        assert hp.primary_url == "https://example.com"
        assert hp.app_clip_on is True
        assert hp.availability_level == 0
        assert hp.drive_id == "drive-1"

    def test_parses_qr_code(self, hub_profile_payload: dict) -> None:
        hp = GetHubProfile.model_validate(hub_profile_payload)

        assert isinstance(hp.qr_code, HubProfileQrCode)
        assert hp.qr_code.target_url == "https://example.com"
        assert hp.qr_code.qr_code_url == "https://qr.example.com/code.png"

    def test_parses_buttons(self, hub_profile_payload: dict) -> None:
        hp = GetHubProfile.model_validate(hub_profile_payload)

        assert len(hp.buttons) == 1
        btn = hp.buttons[0]
        assert isinstance(btn, ActionButtonResponse)
        assert btn.title == "Join"
        assert btn.hidden is False
        assert btn.logic.dollar_type == "BecomeMember"

    def test_defaults_for_optional_fields(self) -> None:
        hp = GetHubProfile.model_validate({"id": "x", "name": "X", "userName": "x"})
        assert hp.sub_name is None
        assert hp.app_clip_on is False
        assert hp.buttons == []
        assert hp.widgets == []
        assert hp.qr_code is None


class TestHubProfileChannel:
    def test_parses_permission_fields(self, channel_payload: dict) -> None:
        ch = HubProfileChannel.model_validate(channel_payload)

        assert ch.is_archived is False
        assert ch.can_edit is True
        assert ch.can_manage is True
        assert ch.can_archive is False
        assert ch.hub_profile_name == "Test Profile"

    def test_defaults_to_false(self) -> None:
        ch = HubProfileChannel.model_validate({"id": "x", "name": "X"})
        assert ch.is_archived is False
        assert ch.can_edit is False
        assert ch.can_archive is False
        assert ch.can_manage is False


class TestMainPlayableAsset:
    def test_parses_external_media_id(self, content_v2_payload: dict) -> None:
        cv2 = ContentV2.model_validate(content_v2_payload)

        assert cv2.main_asset is not None
        assert cv2.main_asset.external_media_id == "ext-abc"
        assert cv2.main_asset.hls_stream_url == "https://hls.example.com/stream.m3u8"
        assert cv2.main_asset.status == "Ready"

    def test_external_media_id_optional(self) -> None:
        asset = MainPlayableAsset.model_validate(
            {
                "id": "a1",
                "name": "Embed",
                "$type": "Embed",
                "url": "https://youtube.com",
            }
        )
        assert asset.external_media_id is None


class TestWorkspaceUser:
    def test_parses_nested_profile(self, workspace_user_payload: dict) -> None:
        user = WorkspaceUser.model_validate(workspace_user_payload)

        assert user.id == "user-1"
        assert user.profile.email == "user@example.com"
        assert user.profile.first_name == "John"
        assert user.profile.last_name == "Doe"
        assert user.profile.avatar_url is None

    def test_parses_role_objects(self, workspace_user_payload: dict) -> None:
        user = WorkspaceUser.model_validate(workspace_user_payload)

        assert user.hub_profile_highest_role.id == 1
        assert user.hub_profile_highest_role.name == "HubProfileViewer"
        assert user.workspace_role is None

    def test_workspace_role_populated(self, workspace_user_payload: dict) -> None:
        workspace_user_payload["workspaceRole"] = {"id": 1, "name": "WorkspaceAdmin"}
        user = WorkspaceUser.model_validate(workspace_user_payload)

        assert user.workspace_role is not None
        assert user.workspace_role.name == "WorkspaceAdmin"
