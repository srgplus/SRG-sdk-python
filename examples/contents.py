# flake8: noqa: T201
"""
Contents — create / update / delete / sections / progressions examples.
"""

from srg import SRGClient
from srg.schemas.content import ContentChannelUpsert

client = SRGClient(api_key="SRG_API_KEY")

HUB_PROFILE_ID = "your-hub-profile-id"
CHANNEL_ID = "your-channel-id"
CATEGORY_ID = "your-category-id"

# ── Create ────────────────────────────────────────────────────────────────────

# --- Minimal ---
result = client.contents.create(
    name="Welcome to the Team",
    hub_profile_id=HUB_PROFILE_ID,
)
content_id = result.id
print("Created:", content_id)

# --- With channel placement ---
result = client.contents.create(
    name="Intro Video",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Public",
    details="Everything you need for day one.",
    channels=[CHANNEL_ID],
)
print("Created with channel:", result.id)

# --- With explicit category placement ---
result = client.contents.create(
    name="Policy Document",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Private",
    channels=[
        ContentChannelUpsert(channel_id=CHANNEL_ID, category_ids=[CATEGORY_ID]),
    ],
)
print("Created with category:", result.id)

# --- With main asset ---
ASSET_ID = "your-asset-id"
result = client.contents.create(
    name="Training Video",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Public",
    main_asset_id=ASSET_ID,
    channels=[CHANNEL_ID],
)
print("Created with asset:", result.id)

# ── Read ──────────────────────────────────────────────────────────────────────

# --- Get v1 (basic metadata) ---
content = client.contents.get(content_id)
print("Get v1:", content.name, content.privacy)

# --- Get v2 (includes main asset + progression) ---
content_v2 = client.contents.get_v2(content_id)
if content_v2.main_asset:
    print(
        "Main asset:", content_v2.main_asset.id, content_v2.main_asset.external_media_id
    )

# --- Filter — single page (manual cursor control) ---
page = client.contents.filter(HUB_PROFILE_ID, page_size=20, types=["Content"])
for item in page.items:
    print("Filter:", item.name)

if page.cursor:
    page2 = client.contents.filter(HUB_PROFILE_ID, page_size=20, cursor=page.cursor)

# --- Filter — iterate all pages automatically ---
for item in client.contents.filter_all(HUB_PROFILE_ID, page_size=50):
    print("All:", item.name)

# --- Search — returns all results in a single request ---
for item in client.contents.search_all(HUB_PROFILE_ID, search="welcome"):
    print("Search:", item.name)

# ── Update ────────────────────────────────────────────────────────────────────

updated = client.contents.update(
    content_id,
    name="Welcome to the Team (v2)",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Public",
    details="Updated onboarding guide.",
    channels=[CHANNEL_ID],
)
print("Updated:", updated.id)

# ── Category management ───────────────────────────────────────────────────────

# --- Add to additional category ---
client.contents.add_to_categories(
    content_id,
    body={
        "contentId": content_id,
        "channels": [
            {
                "channelId": CHANNEL_ID,
                "categoryIds": [CATEGORY_ID],
            }
        ],
    },
)
print("Added to category")

# --- Remove from category ---
client.contents.remove_from_categories(
    content_id,
    body={
        "contentId": content_id,
        "channels": [
            {
                "channelId": CHANNEL_ID,
                "categoryIds": [CATEGORY_ID],
            }
        ],
    },
)
print("Removed from category")

# --- Move between categories ---
OTHER_CATEGORY_ID = "other-category-id"
client.contents.move(
    content_id,
    body={
        "contentId": content_id,
        "channelId": CHANNEL_ID,
        "fromCategoryId": CATEGORY_ID,
        "toCategoryId": OTHER_CATEGORY_ID,
    },
)
print("Moved to other category")

# ── Sections (collections only) ───────────────────────────────────────────────

# --- Create section ---
client.contents.create_section(content_id, "media", name="Day 1 — Intro")
print("Created section")

# --- Update section ---
SECTION_ID = "your-section-id"
client.contents.update_section(content_id, "media", SECTION_ID, name="Day 1 — Overview")
print("Updated section")

# --- Delete section ---
client.contents.delete_section(content_id, "media", SECTION_ID)
print("Deleted section")

# ── Progressions ──────────────────────────────────────────────────────────────

# --- Update content progression ---
progression = client.contents.patch_content_progression(content_id, status="Completed")
print("Progression:", progression.status)

# --- Update media playback position (call periodically during playback) ---
MEDIA_ID = "your-media-id"
client.contents.patch_media_progression(MEDIA_ID, last_watched_time=95)
print("Saved playback position")

# --- Get progression stats (scoped to a collection) ---
COLLECTION_ID = "your-collection-id"
stats = client.contents.get_progression_stats(collection_id=COLLECTION_ID)
print(f"Progress: {stats.completed}/{stats.total}")

# --- Get global progression stats ---
stats = client.contents.get_progression_stats()
print(f"Global progress: {stats.completed}/{stats.total}")
