# flake8: noqa: T201
"""
Hub Profiles — create / update / delete / archive / restore examples.
"""

from srg import SRGClient
from srg.schemas.hub_profile import ActionButtonLogicUpsert, ActionButtonUpsert

client = SRGClient(api_key="SRG_API_KEY")

WORKSPACE_ID = "your-workspace-id"

# --- Create (minimal) ---
result = client.hub_profiles.create(
    name="Acme Academy",
    user_name="acme-academy",
    workspace_id=WORKSPACE_ID,
)
hub_profile_id = result.id
print("Created:", hub_profile_id)

# --- Create with avatar + cover (auto-upload) ---
profile = client.hub_profiles.create(
    name="Beta Hub",
    user_name="beta-hub",
    description="A hub for beta testers.",
    availability_level="Public",
    avatar_image="/path/to/avatar.jpg",
    cover_image="/path/to/cover.png",
    workspace_id=WORKSPACE_ID,
)
print("Created with images:", profile.id, profile.avatar)

# --- Create with action buttons ---
profile_with_buttons = client.hub_profiles.create(
    name="Acme Sales Hub",
    user_name="acme-sales",
    buttons=[
        ActionButtonUpsert(
            title="Visit Website",
            logic=ActionButtonLogicUpsert(
                type="ExternalLink", url="https://acme.example.com"
            ),
        ),
    ],
    workspace_id=WORKSPACE_ID,
)
print("Created with buttons:", profile_with_buttons.id)

# --- Get by ID ---
profile = client.hub_profiles.get(hub_profile_id)
print("Get:", profile.name, profile.user_name)

# --- Get by username ---
profile = client.hub_profiles.get_by_username("acme-academy")
print("Get by username:", profile.id)

# --- List all in workspace ---
profiles = client.hub_profiles.list()
for p in profiles:
    print("List:", p.id, p.name)

# --- List managed (where current user is Admin/Editor) ---
managed = client.hub_profiles.list_managed()
for p in managed:
    print("Managed:", p.id, p.name)

# --- Filter by IDs ---
filtered = client.hub_profiles.filter(ids=[hub_profile_id])
for p in filtered:
    print("Filter:", p.id, p.name)

# --- Update (no images) ---
client.hub_profiles.update(
    hub_profile_id,
    name="Acme Academy (Updated)",
    user_name="acme-academy",
    description="Updated description.",
    availability_level="Private",
)
print("Updated name")

# --- Update with new avatar (auto-upload) ---
profile = client.hub_profiles.update(
    hub_profile_id,
    name="Acme Academy",
    user_name="acme-academy",
    avatar_image="/path/to/new_avatar.jpg",
)
print("Updated avatar:", profile.avatar)

# --- Join (register current user as member) ---
client.hub_profiles.join(hub_profile_id)
print("Joined hub profile")

# --- Archive ---
client.hub_profiles.archive(hub_profile_id)
print("Archived")

# --- Restore ---
client.hub_profiles.restore(hub_profile_id)
print("Restored")

# --- Move to another workspace ---
OTHER_WORKSPACE_ID = "other-workspace-id"
client.hub_profiles.move_to_workspace(hub_profile_id, OTHER_WORKSPACE_ID)
print("Moved to workspace")

# --- Delete permanently ---
client.hub_profiles.delete(hub_profile_id)
print("Deleted")
