from datetime import datetime
from typing import Any

from pydantic import Field

from srg.schemas.common import Cover, SignedUrl, SRGModel


class ActionButtonLogicUpsert(SRGModel):
    """Logic for an action button (e.g., URL link)."""

    type: str
    url: str | None = None
    data: dict[str, Any] | None = None


class ActionButtonUpsert(SRGModel):
    title: str
    logic: ActionButtonLogicUpsert


class ActionLogicResponse(SRGModel):
    """Polymorphic logic returned inside ActionButtonResponse."""

    dollar_type: str = Field(alias="$type")
    url: str | None = None
    data: dict[str, Any] | None = None


class ActionButtonResponse(SRGModel):
    title: str
    hidden: bool = False
    logic: ActionLogicResponse


class HubProfileQrCode(SRGModel):
    target_url: str
    qr_code_url: str


class GetHubProfile(SRGModel):
    id: str
    name: str
    user_name: str
    workspace_id: str | None = None
    drive_id: str | None = None
    sub_name: str | None = None
    description: str | None = None
    primary_url: str | None = None
    app_clip_on: bool = False
    availability_level: int | None = None  # 0=Public, 1=Private
    avatar: Cover | None = None
    cover: Cover | None = None
    qr_code: HubProfileQrCode | None = None
    buttons: list[ActionButtonResponse] = Field(default_factory=list)
    widgets: list[Any] = Field(default_factory=list)  # noqa: ANN401


class MinimalHubProfile(SRGModel):
    id: str
    name: str
    user_name: str
    workspace_id: str | None = None
    drive_id: str | None = None
    avatar: Cover | None = None


class HubProfileSignedUrls(SRGModel):
    id: str
    avatar_signed_url: SignedUrl | None = None
    cover_signed_url: SignedUrl | None = None
    avatar_extension: str | None = None
    cover_extension: str | None = None
    widgets: list[dict[str, Any]] = Field(default_factory=list)


class HubProfileAvatar(SRGModel):
    """Avatar shape returned by the filter endpoint."""

    path: str | None = None
    modified: datetime | None = None


class HubProfileFilter(SRGModel):
    """Item returned by POST /hub-profiles/filter."""

    id: str
    name: str
    user_name: str
    avatar: HubProfileAvatar | None = None
