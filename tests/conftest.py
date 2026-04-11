from unittest.mock import AsyncMock, Mock

import pytest

from srg._http import AsyncHTTPClient, SyncHTTPClient


@pytest.fixture
def mock_http() -> Mock:
    return Mock(spec=SyncHTTPClient)


@pytest.fixture
def async_mock_http() -> AsyncMock:
    return AsyncMock(spec=AsyncHTTPClient)


# --- Sample data payloads (match real camelCase JSON from backend) ---

CONTENT_ID = "content-uuid-1"
HUB_PROFILE_ID = "hub-profile-uuid-1"
CHANNEL_ID = "channel-uuid-1"
ASSET_ID = "asset-uuid-1"
WORKSPACE_ID = "workspace-uuid-1"


@pytest.fixture
def content_payload() -> dict:
    return {
        "id": CONTENT_ID,
        "name": "My Content",
        "details": "Some details",
        "url": None,
        "createdBy": "user-1",
        "hubProfileId": HUB_PROFILE_ID,
        "hubProfileName": "Test Profile",
        "created": "2024-01-01T00:00:00Z",
        "archived": None,
        "cover": None,
        "channels": [],
        "headingReferencedContent": [],
    }


@pytest.fixture
def content_v2_payload() -> dict:
    return {
        "id": CONTENT_ID,
        "privacy": "Public",
        "name": "My Content",
        "details": "Existing details",
        "url": "https://example.com",
        "createdBy": "user-1",
        "hubProfileId": HUB_PROFILE_ID,
        "created": "2024-01-01T00:00:00Z",
        "mainAsset": {
            "$type": "Media",
            "id": "asset-1",
            "name": "Video",
            "cover": None,
            "durationInSeconds": 120,
            "externalMediaId": "ext-abc",
            "hlsStreamUrl": "https://hls.example.com/stream.m3u8",
            "originalStreamUrl": "https://origin.example.com/video.mp4",
            "status": "Ready",
            "progression": None,
        },
        "channels": [
            {
                "id": CHANNEL_ID,
                "name": "Main Channel",
                "categories": [
                    {"id": "cat-1", "name": "Basics"},
                    {"id": "cat-2", "name": "Advanced"},
                ],
            }
        ],
        "context": [
            {"$type": "Text", "id": "widget-1", "title": "Intro", "content": "Hello"},
            {"$type": "Media", "id": "widget-2", "title": None, "assetId": "asset-1"},
        ],
        "categories": [{"id": "cat-1"}, {"id": "cat-2"}],
    }


@pytest.fixture
def hub_profile_payload() -> dict:
    return {
        "id": HUB_PROFILE_ID,
        "name": "Test Profile",
        "userName": "test-profile",
        "workspaceId": WORKSPACE_ID,
        "driveId": "drive-1",
        "subName": "Sub",
        "description": "A description",
        "primaryUrl": "https://example.com",
        "appClipOn": True,
        "availabilityLevel": 0,
        "canArchive": False,
        "canManage": True,
        "isArchived": False,
        "avatar": None,
        "cover": None,
        "qrCode": {
            "targetUrl": "https://example.com",
            "qrCodeUrl": "https://qr.example.com/code.png",
        },
        "buttons": [
            {
                "title": "Join",
                "hidden": False,
                "logic": {"$type": "BecomeMember", "url": None},
            }
        ],
        "widgets": [],
    }


@pytest.fixture
def channel_payload() -> dict:
    return {
        "id": CHANNEL_ID,
        "name": "Main Channel",
        "privacy": "Public",
        "hubProfileId": HUB_PROFILE_ID,
        "hubProfileName": "Test Profile",
        "hubProfileUserName": "test-profile",
        "isArchived": False,
        "canEdit": True,
        "canArchive": False,
        "canManage": True,
        "categories": [],
    }


@pytest.fixture
def workspace_user_payload() -> dict:
    return {
        "id": "user-1",
        "hubProfileHighestRole": {"id": 1, "name": "HubProfileViewer"},
        "workspaceRole": None,
        "profile": {
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe",
            "avatarUrl": None,
        },
    }
