<a id="srg.resources.users"></a>

# srg.resources.users

<a id="srg.resources.users.UsersResource"></a>

## UsersResource Objects

```python
class UsersResource()
```

<a id="srg.resources.users.UsersResource.get"></a>

#### get

```python
def get(user_id: str) -> UserFullProfile
```

Get user profile by ID.

Retrieves the full public profile of a user, including their name,
email address, phone number, and avatar.

**Arguments**:

- `user_id` - The ID of the user to retrieve.
  

**Returns**:

  UserFullProfile containing the user's profile data.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
user = client.users.get("01965f7a-0000-7000-8000-000000000007")
```
  
  Example response:
```python
UserFullProfile(
    id="01965f7a-0000-7000-8000-000000000007",
    profile=FullProfile(
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone_number="+1234567890",
        avatar_url=Cover(
            details=CoverDetails(
                url="https://cdn.srgplus.com/avatars/john-doe.jpg",
                extension="jpg",
            ),
            modified="2025-06-01T10:00:00Z",
        ),
    ),
)
```
<a id="srg.resources.users.UsersResource.check_exists_with_email"></a>

#### check\_exists\_with\_email

```python
def check_exists_with_email(email: str) -> bool
```

Check whether a user with the given email exists.

Returns True if a registered user account is associated with the
provided email address, False otherwise.

**Arguments**:

- `email` - Email address to check.
  

**Returns**:

  True if a user with that email exists, False otherwise.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
exists = client.users.check_exists_with_email("john.doe@example.com")
```
  
  Example response:
```python
True
```
<a id="srg.resources.users.UsersResource.check_exists_with_phone"></a>

#### check\_exists\_with\_phone

```python
def check_exists_with_phone(phone_number: str) -> bool
```

Check whether a user with the given phone number exists.

Returns True if a registered user account is associated with the
provided phone number, False otherwise.

**Arguments**:

- `phone_number` - Phone number to check (e.g. ``"+1234567890"``).
  

**Returns**:

  True if a user with that phone number exists, False otherwise.
  

**Example**:

```python
client = SRGClient(api_key="srgplus_your_key")
exists = client.users.check_exists_with_phone("+1234567890")
```
  
  Example response:
```python
False
```
<a id="srg.resources.users.AsyncUsersResource"></a>

## AsyncUsersResource Objects

```python
class AsyncUsersResource()
```

<a id="srg.resources.users.AsyncUsersResource.get"></a>

#### get

```python
async def get(user_id: str) -> UserFullProfile
```

Get user profile by ID.

Retrieves the full public profile of a user, including their name,
email address, phone number, and avatar.

**Arguments**:

- `user_id` - The ID of the user to retrieve.
  

**Returns**:

  UserFullProfile containing the user's profile data.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    user = await client.users.get("01965f7a-0000-7000-8000-000000000007")
```
  
  Example response:
```python
UserFullProfile(
    id="01965f7a-0000-7000-8000-000000000007",
    profile=FullProfile(
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone_number="+1234567890",
        avatar_url=Cover(
            details=CoverDetails(
                url="https://cdn.srgplus.com/avatars/john-doe.jpg",
                extension="jpg",
            ),
            modified="2025-06-01T10:00:00Z",
        ),
    ),
)
```
<a id="srg.resources.users.AsyncUsersResource.check_exists_with_email"></a>

#### check\_exists\_with\_email

```python
async def check_exists_with_email(email: str) -> bool
```

Check whether a user with the given email exists.

Returns True if a registered user account is associated with the
provided email address, False otherwise.

**Arguments**:

- `email` - Email address to check.
  

**Returns**:

  True if a user with that email exists, False otherwise.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    exists = await client.users.check_exists_with_email("john.doe@example.com")
```
  
  Example response:
```python
True
```
<a id="srg.resources.users.AsyncUsersResource.check_exists_with_phone"></a>

#### check\_exists\_with\_phone

```python
async def check_exists_with_phone(phone_number: str) -> bool
```

Check whether a user with the given phone number exists.

Returns True if a registered user account is associated with the
provided phone number, False otherwise.

**Arguments**:

- `phone_number` - Phone number to check (e.g. ``"+1234567890"``).
  

**Returns**:

  True if a user with that phone number exists, False otherwise.
  

**Example**:

```python
async with AsyncSRGClient(api_key="srgplus_your_key") as client:
    exists = await client.users.check_exists_with_phone("+1234567890")
```
  
  Example response:
```python
False
```