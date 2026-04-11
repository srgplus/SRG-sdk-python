# flake8: noqa: T201
import asyncio
import os

from srg import AsyncSRGClient


async def main() -> None:
    async with AsyncSRGClient(api_key=os.environ["SRG_API_KEY"]) as client:
        HUB_PROFILE_ID = "your-hub-profile-id"

        # Get hub profile
        profile = await client.hub_profiles.get(HUB_PROFILE_ID)
        print(profile.name, profile.availability_level)

        # Iterate all content pages
        async for content in client.contents.filter_all(HUB_PROFILE_ID, page_size=50):
            print(content.name)

        # Workspace users
        workspace_id = "your-workspace-id"
        users = await client.workspaces.get_users(workspace_id)
        for user in users:
            print(user.profile.email, user.hub_profile_highest_role.name)


if __name__ == "__main__":
    asyncio.run(main())
