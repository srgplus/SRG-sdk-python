from srg.schemas.common import Cover, SRGModel


class PublicProfile(SRGModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: Cover | None = None


class FullProfile(PublicProfile):
    phone_number: str | None = None


class UserFullProfile(SRGModel):
    id: str
    profile: FullProfile


class ExistsWithEmail(SRGModel):
    exists: bool


class ExistsWithPhone(SRGModel):
    exists: bool
