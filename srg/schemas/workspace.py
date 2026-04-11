from pydantic import Field

from srg.schemas.common import Cover, SignedUrl, SRGModel
from srg.schemas.hub_profile import MinimalHubProfile


class Seat(SRGModel):
    name: str
    users_count: int
    limit: int | None


class SubscriptionBillingData(SRGModel):
    next_billing_date: str | None = None
    amount: float | None = None
    currency: str | None = None


class SubscriptionDetails(SRGModel):
    subscription_plan: str
    customer_portal_url: str | None
    billing_data: SubscriptionBillingData | None


class WorkspaceHubProfile(SRGModel):
    id: str
    name: str
    user_name: str
    avatar: Cover | None = None


class Workspace(SRGModel):
    id: str
    name: str
    cover: Cover | None = None
    seats: list[Seat] = Field(default_factory=list)
    memory_usage: int = 0
    subscription_details: SubscriptionDetails | None = None
    hub_profiles: list[WorkspaceHubProfile] = Field(default_factory=list)


class WorkspaceSignedUrl(SRGModel):
    id: str
    cover_signed_url: SignedUrl | None = None
    cover_extension: str | None = None


class ProgressionUpdatedMetadata(SRGModel):
    """
    Action metadata discriminated by $type == 'ProgressionUpdatedMetadata'
    """

    dollar_type: str = Field("ProgressionUpdatedMetadata", alias="$type")
    webhook_url: str


class ActionMetadata(SRGModel):
    dollar_type: str = Field(alias="$type")
    webhook_url: str | None = None

    model_config = SRGModel.model_config


class Action(SRGModel):
    id: str
    title: str
    workspace_id: str
    details: str | None
    action_metadata: ActionMetadata | None = None
    hub_profiles: list[MinimalHubProfile] = Field(default_factory=list)


class MinimalAction(SRGModel):
    id: str
    title: str
    workspace_id: str
    details: str | None = None
