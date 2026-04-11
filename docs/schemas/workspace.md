## Action

*model* `Action(id, title, workspace_id, details, action_metadata=None, hub_profiles=[])`

**Fields**

- **id** (*str*)
- **title** (*str*)
- **workspace_id** (*str*)
- **details** (*str | None*)
- **action_metadata** (*ActionMetadata | None, optional*) – Defaults to `None`.
- **hub_profiles** (*list[MinimalHubProfile], optional*) – Defaults to `[]`.

## ActionMetadata

*model* `ActionMetadata(dollar_type, webhook_url=None)`

**Fields**

- **dollar_type** (*str*)
- **webhook_url** (*str | None, optional*) – Defaults to `None`.

## MinimalAction

*model* `MinimalAction(id, title, workspace_id, details=None)`

**Fields**

- **id** (*str*)
- **title** (*str*)
- **workspace_id** (*str*)
- **details** (*str | None, optional*) – Defaults to `None`.

## ProgressionUpdatedMetadata

*model* `ProgressionUpdatedMetadata(dollar_type='ProgressionUpdatedMetadata', webhook_url)`

Action metadata discriminated by $type == 'ProgressionUpdatedMetadata'

**Fields**

- **dollar_type** (*str, optional*) – Defaults to `'ProgressionUpdatedMetadata'`.
- **webhook_url** (*str*)

## Seat

*model* `Seat(name, users_count, limit)`

**Fields**

- **name** (*str*)
- **users_count** (*int*)
- **limit** (*int | None*)

## SubscriptionBillingData

*model* `SubscriptionBillingData(next_billing_date=None, amount=None, currency=None)`

**Fields**

- **next_billing_date** (*str | None, optional*) – Defaults to `None`.
- **amount** (*float | None, optional*) – Defaults to `None`.
- **currency** (*str | None, optional*) – Defaults to `None`.

## SubscriptionDetails

*model* `SubscriptionDetails(subscription_plan, customer_portal_url, billing_data)`

**Fields**

- **subscription_plan** (*str*)
- **customer_portal_url** (*str | None*)
- **billing_data** (*SubscriptionBillingData | None*)

## Workspace

*model* `Workspace(id, name, cover=None, seats=[], memory_usage=0, subscription_details=None, hub_profiles=[])`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **cover** (*Cover | None, optional*) – Defaults to `None`.
- **seats** (*list[Seat], optional*) – Defaults to `[]`.
- **memory_usage** (*int, optional*) – Defaults to `0`.
- **subscription_details** (*SubscriptionDetails | None, optional*) – Defaults to `None`.
- **hub_profiles** (*list[WorkspaceHubProfile], optional*) – Defaults to `[]`.

## WorkspaceHubProfile

*model* `WorkspaceHubProfile(id, name, user_name, avatar=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **user_name** (*str*)
- **avatar** (*Cover | None, optional*) – Defaults to `None`.

## WorkspaceSignedUrl

*model* `WorkspaceSignedUrl(id, cover_signed_url=None, cover_extension=None)`

**Fields**

- **id** (*str*)
- **cover_signed_url** (*SignedUrl | None, optional*) – Defaults to `None`.
- **cover_extension** (*str | None, optional*) – Defaults to `None`.
