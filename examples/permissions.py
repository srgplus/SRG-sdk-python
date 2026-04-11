# flake8: noqa: T201
"""
Permissions, Permission Groups & Invitations — full CRUD examples.

Role IDs (typical):
  1 — Admin
  2 — Editor
  3 — Viewer

Target types:
  "HubProfile", "Workspace", "Channel"
"""

from srg import SRGClient

client = SRGClient(api_key="SRG_API_KEY")

WORKSPACE_ID = "your-workspace-id"
HUB_PROFILE_ID = "your-hub-profile-id"
USER_ID = "your-user-id"

# ── Permissions ───────────────────────────────────────────────────────────────

# --- Give a role ---
client.permissions.give(
    user_id=USER_ID,
    target_id=HUB_PROFILE_ID,
    target_type="HubProfile",
    role_id=2,  # Editor
)
print("Gave Editor role")

# --- Check access ---
can_read = client.permissions.can_read(
    target_id=HUB_PROFILE_ID, target_type="HubProfile"
)
can_edit = client.permissions.can_edit(
    target_id=HUB_PROFILE_ID, target_type="HubProfile"
)
can_manage = client.permissions.can_manage_permissions(
    target_id=HUB_PROFILE_ID, target_type="HubProfile"
)
is_member = client.permissions.is_member(
    target_id=HUB_PROFILE_ID, target_type="HubProfile"
)
print(f"Access: read={can_read} edit={can_edit} manage={can_manage} member={is_member}")

# --- Get all targets the current user has access to ---
targets = client.permissions.get_targets("HubProfile")
for t in targets:
    print("Target:", t.target_id)

# --- Get all users in a workspace ---
users = client.permissions.get_workspace_users(WORKSPACE_ID)
for u in users:
    print("Workspace user:", u.profile.email, u.hub_profile_highest_role.name)

# --- Revoke role ---
client.permissions.delete(
    target_type="HubProfile",
    target_id=HUB_PROFILE_ID,
    user_id=USER_ID,
)
print("Revoked role")

# ── Permission Groups ─────────────────────────────────────────────────────────

# --- Create ---
group_id = client.permission_groups.create(
    "HubProfile",
    HUB_PROFILE_ID,
    name="Content Editors",
)
print("Created group:", group_id)

# --- List ---
groups = client.permission_groups.list("HubProfile", HUB_PROFILE_ID)
for g in groups:
    print("Group:", g.id, g.name, "users:", g.total_users)

# --- Get (with members) ---
group = client.permission_groups.get(group_id)
print("Group members:")
for u in group.users:
    print(" ", u.email, u.first_name, u.last_name)

# --- Update name ---
client.permission_groups.update(group_id, name="Senior Editors")
print("Renamed group")

# --- Add users ---
OTHER_USER_ID = "another-user-id"
client.permission_groups.add_users(
    group_id,
    user_ids=[USER_ID, OTHER_USER_ID],
)
print("Added users to group")

# --- Remove a user ---
client.permission_groups.remove_user(group_id, OTHER_USER_ID)
print("Removed user from group")

# --- Delete ---
client.permission_groups.delete(group_id)
print("Deleted group")

# ── Invitations ───────────────────────────────────────────────────────────────

# --- Invite by email(s) ---
result = client.invitations.invite(
    "HubProfile",
    HUB_PROFILE_ID,
    role_id=2,
    emails=["alice@example.com", "bob@example.com"],
)
invitation_id = result.ids[0]
print("Invited:", result.ids)

# --- Create invitation link (single email) ---
link_result = client.invitations.invite_with_link(
    "HubProfile",
    HUB_PROFILE_ID,
    role_id=3,
    email="charlie@example.com",
)
print("Invite link:", link_result.access_link)

# --- List pending invitations ---
invitations = client.invitations.list("HubProfile", HUB_PROFILE_ID)
for inv in invitations:
    print("Pending:", inv.id, inv.email, inv.role_id, inv.status)

# --- Update role on an invitation ---
client.invitations.update(
    "HubProfile",
    HUB_PROFILE_ID,
    invitation_id,
    role_id=3,  # downgrade to Viewer
)
print("Updated invitation role")

# --- Cancel / delete invitation ---
client.invitations.delete("HubProfile", HUB_PROFILE_ID, invitation_id)
print("Cancelled invitation")

# ── Users ─────────────────────────────────────────────────────────────────────

# --- Get user profile ---
user = client.users.get(USER_ID)
print("User:", user.profile.email, user.profile.first_name)

# --- Check whether email is registered ---
exists = client.users.check_exists_with_email("alice@example.com")
print("Email exists:", exists)

# --- Check whether phone number is registered ---
exists = client.users.check_exists_with_phone("+1234567890")
print("Phone exists:", exists)
