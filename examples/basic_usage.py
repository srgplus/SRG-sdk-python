# flake8: noqa: T201

from srg import SRGClient

client = SRGClient(api_key="SRG_API_KEY")

HUB_PROFILE_ID = "your-hub-profile-id"
CHANNEL_ID = "your-channel-id"

# --- Get hub profile (includes buttons, widgets, qr_code) ---
profile = client.hub_profiles.get("your-hub-profile-id")
print(profile.name, profile.sub_name)
for btn in profile.buttons:
    print(btn.title, btn.logic.dollar_type)

# --- List channels with permissions ---
channels = client.channels.list(HUB_PROFILE_ID)
for ch in channels:
    print(ch.name, "can_edit:", ch.can_edit, "archived:", ch.is_archived)

# --- Create content ---
result = client.contents.create(
    name="My Video",
    hub_profile_id=HUB_PROFILE_ID,
    privacy="Preview",
    channels=[CHANNEL_ID],
)
content_id = result.id

# --- Get V2 (includes main asset with external_media_id) ---
content = client.contents.get_v2(content_id)
if content.main_asset:
    print(content.main_asset.external_media_id)

# --- Iterate all content pages ---
all_contents = list(client.contents.filter_all(HUB_PROFILE_ID, page_size=50))
print(f"Total: {len(all_contents)}")

# --- Progression ---
progression = client.contents.patch_content_progression(content_id, status="Completed")
print(progression.status)

# --- Create section ---
client.contents.create_section(content_id, "media", name="Intro")
