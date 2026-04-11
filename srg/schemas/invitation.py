from srg.schemas.common import SRGModel


class InviteToTarget(SRGModel):
    ids: list[str]


class InviteToHubWithLink(SRGModel):
    invitation_id: str
    access_link: str


class Invitation(SRGModel):
    id: str
    target_id: str
    target_type: str
    email: str | None = None
    role_id: int | None = None
    status: str | None = None
