## Invitation

*model* `Invitation(id, target_id, target_type, email=None, role_id=None, status=None)`

**Fields**

- **id** (*str*)
- **target_id** (*str*)
- **target_type** (*str*)
- **email** (*str | None, optional*) – Defaults to `None`.
- **role_id** (*int | None, optional*) – Defaults to `None`.
- **status** (*str | None, optional*) – Defaults to `None`.

## InviteToHubWithLink

*model* `InviteToHubWithLink(invitation_id, access_link)`

**Fields**

- **invitation_id** (*str*)
- **access_link** (*str*)

## InviteToTarget

*model* `InviteToTarget(ids)`

**Fields**

- **ids** (*list[str]*)
