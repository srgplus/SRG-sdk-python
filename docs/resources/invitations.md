<a id="srg.resources.invitations"></a>

# srg.resources.invitations

<a id="srg.resources.invitations.InvitationsResource"></a>

## InvitationsResource Objects

```python
class InvitationsResource()
```

<a id="srg.resources.invitations.InvitationsResource.list"></a>

#### list

```python
def list(target_type: str, target_id: str) -> list[Invitation]
```

List all pending invitations for a target.

Returns all open (not yet accepted or expired) invitations associated
with the given target resource.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
  

**Returns**:

  List of Invitation objects.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
invitations = client.invitations.list(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
)
```
  
  Example response:
```python
[
    Invitation(
        id="01965f7a-0000-7000-8000-000000000020",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        email="alice@example.com",
        role_id=2,
        status="Pending",
    ),
]
```
<a id="srg.resources.invitations.InvitationsResource.invite"></a>

#### invite

```python
def invite(
    target_type: str,
    target_id: str,
    *,
    role_id: int,
    emails: builtins.list[str]
) -> InviteToTarget
```

Send email invitations to join a target with the given role.

Sends invitation emails to one or more addresses. Each invited user
will receive a link to accept the invitation and gain the specified role.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `role_id` - Role ID to assign to the invited users upon acceptance.
- `emails` - List of email addresses to invite.
  

**Returns**:

  InviteToTarget with the list of created invitation IDs.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
result = client.invitations.invite(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
    role_id=2,
    emails=["alice@example.com", "bob@example.com"],
)
```
  
  Example response:
```python
InviteToTarget(
    ids=[
        "01965f7a-0000-7000-8000-000000000021",
        "01965f7a-0000-7000-8000-000000000022",
    ],
)
```
<a id="srg.resources.invitations.InvitationsResource.invite_with_link"></a>

#### invite\_with\_link

```python
def invite_with_link(
    target_type: str,
    target_id: str,
    *,
    role_id: int,
    email: str
) -> InviteToHubWithLink
```

Create an invitation link for a single email address.

Generates a shareable invitation link for the specified email.
The link grants the recipient access to the target with the given role
when followed.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `role_id` - Role ID to assign upon acceptance.
- `email` - Email address of the recipient.
  

**Returns**:

  InviteToHubWithLink containing the invitation ID and access link.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
result = client.invitations.invite_with_link(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
    role_id=2,
    email="alice@example.com",
)
print(result.access_link)
```
  
  Example response:
```python
InviteToHubWithLink(
    invitation_id="01965f7a-0000-7000-8000-000000000021",
    access_link="https://app.srgplus.com/invite/abc123xyz",
)
```
<a id="srg.resources.invitations.InvitationsResource.update"></a>

#### update

```python
def update(
    target_type: str,
    target_id: str,
    invitation_id: str,
    *,
    role_id: int | None = None
) -> None
```

Update the role assigned to an existing invitation.

Changes the role that will be granted to the invited user upon
acceptance. Only pending invitations can be updated.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `invitation_id` - ID of the invitation to update.
- `role_id` - New role ID to assign. Unchanged if not provided.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.invitations.update(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
    "01965f7a-0000-7000-8000-000000000021",
    role_id=3,
)
```
<a id="srg.resources.invitations.InvitationsResource.delete"></a>

#### delete

```python
def delete(target_type: str, target_id: str, invitation_id: str) -> None
```

Cancel and delete an invitation.

Permanently removes the invitation. The invited user will no longer
be able to accept it via email or link.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `invitation_id` - ID of the invitation to delete.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
client.invitations.delete(
    "HubProfile",
    "01965f7a-0000-7000-8000-000000000002",
    "01965f7a-0000-7000-8000-000000000021",
)
```
<a id="srg.resources.invitations.AsyncInvitationsResource"></a>

## AsyncInvitationsResource Objects

```python
class AsyncInvitationsResource()
```

<a id="srg.resources.invitations.AsyncInvitationsResource.list"></a>

#### list

```python
async def list(target_type: str, target_id: str) -> list[Invitation]
```

List all pending invitations for a target.

Returns all open (not yet accepted or expired) invitations associated
with the given target resource.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
  

**Returns**:

  List of Invitation objects.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    invitations = await client.invitations.list(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
    )
```
  
  Example response:
```python
[
    Invitation(
        id="01965f7a-0000-7000-8000-000000000020",
        target_id="01965f7a-0000-7000-8000-000000000002",
        target_type="HubProfile",
        email="alice@example.com",
        role_id=2,
        status="Pending",
    ),
]
```
<a id="srg.resources.invitations.AsyncInvitationsResource.invite"></a>

#### invite

```python
async def invite(
    target_type: str,
    target_id: str,
    *,
    role_id: int,
    emails: builtins.list[str]
) -> InviteToTarget
```

Send email invitations to join a target with the given role.

Sends invitation emails to one or more addresses. Each invited user
will receive a link to accept the invitation and gain the specified role.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `role_id` - Role ID to assign to the invited users upon acceptance.
- `emails` - List of email addresses to invite.
  

**Returns**:

  InviteToTarget with the list of created invitation IDs.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    result = await client.invitations.invite(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
        role_id=2,
        emails=["alice@example.com", "bob@example.com"],
    )
```
  
  Example response:
```python
InviteToTarget(
    ids=[
        "01965f7a-0000-7000-8000-000000000021",
        "01965f7a-0000-7000-8000-000000000022",
    ],
)
```
<a id="srg.resources.invitations.AsyncInvitationsResource.invite_with_link"></a>

#### invite\_with\_link

```python
async def invite_with_link(
    target_type: str,
    target_id: str,
    *,
    role_id: int,
    email: str
) -> InviteToHubWithLink
```

Create an invitation link for a single email address.

Generates a shareable invitation link for the specified email.
The link grants the recipient access to the target with the given role
when followed.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `role_id` - Role ID to assign upon acceptance.
- `email` - Email address of the recipient.
  

**Returns**:

  InviteToHubWithLink containing the invitation ID and access link.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    result = await client.invitations.invite_with_link(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
        role_id=2,
        email="alice@example.com",
    )
```
  
  Example response:
```python
InviteToHubWithLink(
    invitation_id="01965f7a-0000-7000-8000-000000000021",
    access_link="https://app.srgplus.com/invite/abc123xyz",
)
```
<a id="srg.resources.invitations.AsyncInvitationsResource.update"></a>

#### update

```python
async def update(
    target_type: str,
    target_id: str,
    invitation_id: str,
    *,
    role_id: int | None = None
) -> None
```

Update the role assigned to an existing invitation.

Changes the role that will be granted to the invited user upon
acceptance. Only pending invitations can be updated.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `invitation_id` - ID of the invitation to update.
- `role_id` - New role ID to assign. Unchanged if not provided.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.invitations.update(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
        "01965f7a-0000-7000-8000-000000000021",
        role_id=3,
    )
```
<a id="srg.resources.invitations.AsyncInvitationsResource.delete"></a>

#### delete

```python
async def delete(target_type: str, target_id: str, invitation_id: str) -> None
```

Cancel and delete an invitation.

Permanently removes the invitation. The invited user will no longer
be able to accept it via email or link.

**Arguments**:

- `target_type` - Target type (e.g. ``"HubProfile"``, ``"Workspace"``).
- `target_id` - ID of the target resource.
- `invitation_id` - ID of the invitation to delete.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    await client.invitations.delete(
        "HubProfile",
        "01965f7a-0000-7000-8000-000000000002",
        "01965f7a-0000-7000-8000-000000000021",
    )
```