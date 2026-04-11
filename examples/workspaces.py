# flake8: noqa: T201
"""
Workspaces & Actions — update workspace, create / update / delete actions.
"""

from srg import SRGClient
from srg.schemas.workspace import ProgressionUpdatedMetadata

client = SRGClient(api_key="SRG_API_KEY")

WORKSPACE_ID = "your-workspace-id"
HUB_PROFILE_ID = "your-hub-profile-id"

# ── Workspace ─────────────────────────────────────────────────────────────────

# --- Get ---
workspace = client.workspaces.get(WORKSPACE_ID)
print("Workspace:", workspace.name, workspace.memory_usage)
for seat in workspace.seats:
    print("  Seat:", seat.name, f"{seat.users_count}/{seat.limit}")

# --- Update name only ---
workspace = client.workspaces.update(WORKSPACE_ID, name="Acme Corp (Rebranded)")
print("Updated workspace name")

# --- Update with new cover image (auto-upload) ---
workspace = client.workspaces.update(
    WORKSPACE_ID,
    name="Acme Corp",
    cover_image="/path/to/cover.jpg",
)
print("Updated workspace cover:", workspace.cover)

# --- Get all hub profiles in workspace ---
profiles = client.workspaces.get_hub_profiles(WORKSPACE_ID)
for p in profiles:
    print("Hub profile:", p.id, p.name)

# ── Actions ───────────────────────────────────────────────────────────────────

# --- Create (webhook fires when a user completes any content) ---
action_id = client.workspaces.create_action(
    WORKSPACE_ID,
    title="Notify on completion",
    metadata=ProgressionUpdatedMetadata(
        webhook_url="https://hooks.example.com/srg-completion"
    ),
    hub_profile_ids=[HUB_PROFILE_ID],
    details="Fires when a learner marks content as Completed.",
)
print("Created action:", action_id)

# --- Create without scoping to specific hub profiles (fires for all) ---
action_id_global = client.workspaces.create_action(
    WORKSPACE_ID,
    title="Global completion webhook",
    metadata=ProgressionUpdatedMetadata(webhook_url="https://hooks.example.com/global"),
)
print("Created global action:", action_id_global)

# --- List ---
actions = client.workspaces.list_actions(WORKSPACE_ID)
for a in actions:
    print("Action:", a.id, a.title)

# --- Get ---
action = client.workspaces.get_action(WORKSPACE_ID, action_id)
print("Get action:", action.title, action.action_metadata)

# --- Update ---
client.workspaces.update_action(
    WORKSPACE_ID,
    action_id,
    title="Notify on completion (v2)",
    metadata=ProgressionUpdatedMetadata(webhook_url="https://hooks.example.com/srg-v2"),
    hub_profile_ids=[HUB_PROFILE_ID],
    details="Updated webhook URL.",
)
print("Updated action")

# --- Delete ---
client.workspaces.delete_action(WORKSPACE_ID, action_id)
client.workspaces.delete_action(WORKSPACE_ID, action_id_global)
print("Deleted actions")
