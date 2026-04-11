from srg._http import AsyncHTTPClient, SyncHTTPClient
from srg.schemas.user import ExistsWithEmail, UserFullProfile


class UsersResource:
    def __init__(self, http: SyncHTTPClient) -> None:
        self._http = http

    def get(self, user_id: str) -> UserFullProfile:
        """
        Get user profile by ID.

        Retrieves the full public profile of a user, including their name,
        email address, phone number, and avatar.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            UserFullProfile containing the user's profile data.

        Example:
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
        """
        data = self._http.get(f"/api/v1/users/{user_id}")
        return UserFullProfile.model_validate(data)

    def check_exists_with_email(self, email: str) -> bool:
        """
        Check whether a user with the given email exists.

        Returns True if a registered user account is associated with the
        provided email address, False otherwise.

        Args:
            email: Email address to check.

        Returns:
            True if a user with that email exists, False otherwise.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        exists = client.users.check_exists_with_email("john.doe@example.com")
        ```

        Example response:
        ```python
        True
        ```
        """
        data = self._http.post("/api/v1/users/exists/with-email", json={"email": email})
        return ExistsWithEmail.model_validate(data).exists

    def check_exists_with_phone(self, phone_number: str) -> bool:
        """
        Check whether a user with the given phone number exists.

        Returns True if a registered user account is associated with the
        provided phone number, False otherwise.

        Args:
            phone_number: Phone number to check (e.g. ``"+1234567890"``).

        Returns:
            True if a user with that phone number exists, False otherwise.

        Example:
        ```python
        client = SRGClient(api_key="srgplus_your_key")
        exists = client.users.check_exists_with_phone("+1234567890")
        ```

        Example response:
        ```python
        False
        ```
        """
        data = self._http.post(
            "/api/v1/users/exists/with-phone", json={"phoneNumber": phone_number}
        )
        if isinstance(data, dict):
            return data.get("exists", False)
        return bool(data)


class AsyncUsersResource:
    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    async def get(self, user_id: str) -> UserFullProfile:
        """
        Get user profile by ID.

        Retrieves the full public profile of a user, including their name,
        email address, phone number, and avatar.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            UserFullProfile containing the user's profile data.

        Example:
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
        """
        data = await self._http.get(f"/api/v1/users/{user_id}")
        return UserFullProfile.model_validate(data)

    async def check_exists_with_email(self, email: str) -> bool:
        """
        Check whether a user with the given email exists.

        Returns True if a registered user account is associated with the
        provided email address, False otherwise.

        Args:
            email: Email address to check.

        Returns:
            True if a user with that email exists, False otherwise.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            exists = await client.users.check_exists_with_email("john.doe@example.com")
        ```

        Example response:
        ```python
        True
        ```
        """
        data = await self._http.post(
            "/api/v1/users/exists/with-email", json={"email": email}
        )
        return ExistsWithEmail.model_validate(data).exists

    async def check_exists_with_phone(self, phone_number: str) -> bool:
        """
        Check whether a user with the given phone number exists.

        Returns True if a registered user account is associated with the
        provided phone number, False otherwise.

        Args:
            phone_number: Phone number to check (e.g. ``"+1234567890"``).

        Returns:
            True if a user with that phone number exists, False otherwise.

        Example:
        ```python
        async with AsyncSRGClient(api_key="srgplus_your_key") as client:
            exists = await client.users.check_exists_with_phone("+1234567890")
        ```

        Example response:
        ```python
        False
        ```
        """
        data = await self._http.post(
            "/api/v1/users/exists/with-phone", json={"phoneNumber": phone_number}
        )
        if isinstance(data, dict):
            return data.get("exists", False)
        return bool(data)
