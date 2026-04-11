from srg.schemas.common import SignedUrl, SRGModel


class GetTarget(SRGModel):
    target_id: str
    can_archive: bool = False
    can_manage: bool = False
    can_edit: bool = False


class WorkspaceUserRole(SRGModel):
    """Role object returned as {id, name} from the backend Enumeration."""

    id: int
    name: str


class WorkspaceUserProfile(SRGModel):
    email: str
    first_name: str
    last_name: str
    avatar_url: SignedUrl | None = None


class WorkspaceUser(SRGModel):
    id: str
    hub_profile_highest_role: WorkspaceUserRole
    workspace_role: WorkspaceUserRole | None = None
    profile: WorkspaceUserProfile


class PermissionGroup(SRGModel):
    id: str
    target_id: str
    target_type: str
    total_users: int
    name: str | None = None


class PermissionGroupUser(SRGModel):
    id: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class GetPermissionGroup(SRGModel):
    permission_group: PermissionGroup
    users: list[PermissionGroupUser]
