## ExistsWithEmail

*model* `ExistsWithEmail(exists)`

**Fields**

- **exists** (*bool*)

## ExistsWithPhone

*model* `ExistsWithPhone(exists)`

**Fields**

- **exists** (*bool*)

## FullProfile

*model* `FullProfile(email=None, first_name=None, last_name=None, avatar_url=None, phone_number=None)`

**Fields**

- **email** (*str | None, optional*) – Defaults to `None`.
- **first_name** (*str | None, optional*) – Defaults to `None`.
- **last_name** (*str | None, optional*) – Defaults to `None`.
- **avatar_url** (*Cover | None, optional*) – Defaults to `None`.
- **phone_number** (*str | None, optional*) – Defaults to `None`.

## PublicProfile

*model* `PublicProfile(email=None, first_name=None, last_name=None, avatar_url=None)`

**Fields**

- **email** (*str | None, optional*) – Defaults to `None`.
- **first_name** (*str | None, optional*) – Defaults to `None`.
- **last_name** (*str | None, optional*) – Defaults to `None`.
- **avatar_url** (*Cover | None, optional*) – Defaults to `None`.

## UserFullProfile

*model* `UserFullProfile(id, profile)`

**Fields**

- **id** (*str*)
- **profile** (*FullProfile*)
