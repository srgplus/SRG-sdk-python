# flake8: noqa: T201
"""
Channels & Categories — create / update / delete / archive examples.
"""

from srg import SRGClient
from srg.schemas.channel import (
    CategoryToReorder,
    ChannelCategoryOptionsUpsert,
    SectionBaseCreate,
)

client = SRGClient(api_key="SRG_API_KEY")

HUB_PROFILE_ID = "your-hub-profile-id"

# ── Channels ──────────────────────────────────────────────────────────────────

# --- Create ---
channel_id = client.channels.create(
    name="Onboarding",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Public",
)
print("Created channel:", channel_id)

# --- Get by ID (v2 — includes categories with heading content) ---
channel = client.channels.get(channel_id)
print("Get channel:", channel.name, channel.privacy)

# --- Get by hub profile username + channel name ---
channel = client.channels.get_by_name("acme-academy", "onboarding")
print("Get by name:", channel.id)

# --- List all channels in a hub profile ---
channels = client.channels.list(HUB_PROFILE_ID)
for ch in channels:
    print("List channel:", ch.name, "archived:", ch.is_archived)

# --- List including archived ---
channels = client.channels.list(HUB_PROFILE_ID, include_archived=True)

# --- Update name, privacy and category order ---
client.channels.update(
    channel_id=channel_id,
    hub_profile_id=HUB_PROFILE_ID,
    name="Onboarding (Updated)",
    privacy="Private",
)
print("Updated channel")

# --- Archive ---
client.channels.archive(channel_id)
print("Archived channel")

# --- Delete permanently ---
client.channels.delete(channel_id)
print("Deleted channel")

# ── Categories ────────────────────────────────────────────────────────────────

channel_id = client.channels.create(name="Training", hub_profile_id=HUB_PROFILE_ID)

# --- Create category (basic) ---
category_id = client.channels.create_category(
    channel_id,
    name="Week 1",
    is_pinned=True,
    notifications_enabled=True,
)
print("Created category:", category_id)

# --- Create category with display options ---
category_id_b = client.channels.create_category(
    channel_id,
    name="Week 2",
    options=ChannelCategoryOptionsUpsert(
        view_type="Grid",
        is_expandable=True,
        show_progression=True,
        show_cover=True,
    ),
)
print("Created category with options:", category_id_b)

# --- Create category with initial sections ---
category_id_c = client.channels.create_category(
    channel_id,
    name="Week 3",
    sections=[
        SectionBaseCreate(name="Day 1"),
        SectionBaseCreate(name="Day 2"),
    ],
)
print("Created category with sections:", category_id_c)

# --- Update category ---
client.channels.update_category(
    channel_id,
    category_id,
    name="Week 1 (Updated)",
    is_pinned=False,
    notifications_enabled=False,
    options=ChannelCategoryOptionsUpsert(view_type="List"),
)
print("Updated category")

# --- Reorder categories ---
client.channels.update(
    channel_id=channel_id,
    hub_profile_id=HUB_PROFILE_ID,
    name="Training",
    categories=[
        CategoryToReorder(id=category_id_b, order=0),
        CategoryToReorder(id=category_id, order=1),
    ],
)
print("Reordered categories")

# --- Get content references — single page (manual cursor control) ---
page = client.channels.get_category_references(channel_id, category_id, page_size=20)
for ref in page.items:
    print("Ref:", ref.content_id, "order:", ref.order)

if page.cursor:
    page2 = client.channels.get_category_references(
        channel_id, category_id, page_size=20, cursor=page.cursor
    )

# --- Iterate all pages automatically ---
for ref in client.channels.get_category_references_all(channel_id, category_id):
    print("All refs:", ref.content_id, ref.order)

# --- Archive category ---
client.channels.archive_category(channel_id, category_id)
print("Archived category")

# --- Delete category permanently ---
client.channels.delete_category(channel_id, category_id_b)
print("Deleted category")
