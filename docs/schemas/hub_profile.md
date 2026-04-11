## ActionButtonLogicUpsert

*model* `ActionButtonLogicUpsert(type, url=None, data=None)`

Logic for an action button (e.g., URL link).

**Fields**

- **type** (*str*)
- **url** (*str | None, optional*) – Defaults to `None`.
- **data** (*dict[str, Any] | None, optional*) – Defaults to `None`.

## ActionButtonResponse

*model* `ActionButtonResponse(title, hidden=False, logic)`

**Fields**

- **title** (*str*)
- **hidden** (*bool, optional*) – Defaults to `False`.
- **logic** (*ActionLogicResponse*)

## ActionButtonUpsert

*model* `ActionButtonUpsert(title, logic)`

**Fields**

- **title** (*str*)
- **logic** (*ActionButtonLogicUpsert*)

## ActionLogicResponse

*model* `ActionLogicResponse(dollar_type, url=None, data=None)`

Polymorphic logic returned inside ActionButtonResponse.

**Fields**

- **dollar_type** (*str*)
- **url** (*str | None, optional*) – Defaults to `None`.
- **data** (*dict[str, Any] | None, optional*) – Defaults to `None`.

## GetHubProfile

*model* `GetHubProfile(id, name, user_name, workspace_id=None, drive_id=None, sub_name=None, description=None, primary_url=None, app_clip_on=False, availability_level=None, avatar=None, cover=None, qr_code=None, buttons=[], widgets=[])`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **user_name** (*str*)
- **workspace_id** (*str | None, optional*) – Defaults to `None`.
- **drive_id** (*str | None, optional*) – Defaults to `None`.
- **sub_name** (*str | None, optional*) – Defaults to `None`.
- **description** (*str | None, optional*) – Defaults to `None`.
- **primary_url** (*str | None, optional*) – Defaults to `None`.
- **app_clip_on** (*bool, optional*) – Defaults to `False`.
- **availability_level** (*int | None, optional*) – Defaults to `None`.
- **avatar** (*Cover | None, optional*) – Defaults to `None`.
- **cover** (*Cover | None, optional*) – Defaults to `None`.
- **qr_code** (*HubProfileQrCode | None, optional*) – Defaults to `None`.
- **buttons** (*list[ActionButtonResponse], optional*) – Defaults to `[]`.
- **widgets** (*list[Any], optional*) – Defaults to `[]`.

## HubProfileAvatar

*model* `HubProfileAvatar(path=None, modified=None)`

Avatar shape returned by the filter endpoint.

**Fields**

- **path** (*str | None, optional*) – Defaults to `None`.
- **modified** (*datetime | None, optional*) – Defaults to `None`.

## HubProfileFilter

*model* `HubProfileFilter(id, name, user_name, avatar=None)`

Item returned by POST /hub-profiles/filter.

**Fields**

- **id** (*str*)
- **name** (*str*)
- **user_name** (*str*)
- **avatar** (*HubProfileAvatar | None, optional*) – Defaults to `None`.

## HubProfileQrCode

*model* `HubProfileQrCode(target_url, qr_code_url)`

**Fields**

- **target_url** (*str*)
- **qr_code_url** (*str*)

## HubProfileSignedUrls

*model* `HubProfileSignedUrls(id, avatar_signed_url=None, cover_signed_url=None, avatar_extension=None, cover_extension=None, widgets=[])`

**Fields**

- **id** (*str*)
- **avatar_signed_url** (*SignedUrl | None, optional*) – Defaults to `None`.
- **cover_signed_url** (*SignedUrl | None, optional*) – Defaults to `None`.
- **avatar_extension** (*str | None, optional*) – Defaults to `None`.
- **cover_extension** (*str | None, optional*) – Defaults to `None`.
- **widgets** (*list[dict[str, Any]], optional*) – Defaults to `[]`.

## MinimalHubProfile

*model* `MinimalHubProfile(id, name, user_name, workspace_id=None, drive_id=None, avatar=None)`

**Fields**

- **id** (*str*)
- **name** (*str*)
- **user_name** (*str*)
- **workspace_id** (*str | None, optional*) – Defaults to `None`.
- **drive_id** (*str | None, optional*) – Defaults to `None`.
- **avatar** (*Cover | None, optional*) – Defaults to `None`.
