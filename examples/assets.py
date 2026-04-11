# flake8: noqa: T201
"""
Assets — create / update / search / filter examples.

Asset types:
  MediaAssetCreate   — video processed via transcoding pipeline
  EmbedAssetCreate   — external embed (YouTube, Vimeo, …)
  FileAssetCreate    — arbitrary file (PDF, ZIP, …)
  ImageAssetCreate   — image file
  VideoAssetCreate   — raw video file (no transcoding)
"""

from srg import SRGClient
from srg.schemas.asset import (
    EmbedAssetCreate,
    FileAssetCreate,
    ImageAssetCreate,
    MediaAssetCreate,
    VideoAssetCreate,
)

client = SRGClient(api_key="SRG_API_KEY")

HUB_PROFILE_ID = "your-hub-profile-id"

# ── Create (single) ───────────────────────────────────────────────────────────

# --- Media (video, transcoding pipeline) ---
media = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=MediaAssetCreate(
        name="Intro Video",
        duration_in_seconds=120.0,
        memory_size_in_bytes=52_428_800,
    ),
)
print("Created media:", media.id, getattr(media, "status", None))

# --- Embed (YouTube / Vimeo / …) ---
embed = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=EmbedAssetCreate(
        name="Company Overview",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ),
)
print("Created embed:", embed.id)

# --- File (PDF, ZIP, …) ---
file_asset = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=FileAssetCreate(
        name="Employee Handbook",
        extension="pdf",
        memory_size_in_bytes=204_800,
    ),
)
print("Created file:", file_asset.id)

# --- Image ---
image = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=ImageAssetCreate(
        name="Welcome Banner",
        extension="png",
        width=1920.0,
        height=1080.0,
        memory_size_in_bytes=512_000,
    ),
)
print("Created image:", image.id)

# --- Raw video (no transcoding) ---
video = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=VideoAssetCreate(
        name="Raw Recording",
        extension="mp4",
        memory_size_in_bytes=104_857_600,
    ),
)
print("Created video:", video.id)

# ── Create (batch) ────────────────────────────────────────────────────────────

assets = client.assets.create_batch(
    hub_profile_id=HUB_PROFILE_ID,
    assets=[
        FileAssetCreate(
            name="Handbook v2.pdf", extension="pdf", memory_size_in_bytes=210_000
        ),
        ImageAssetCreate(
            name="Logo",
            extension="png",
            width=400.0,
            height=400.0,
            memory_size_in_bytes=48_000,
        ),
    ],
)
for a in assets:
    print("Batch created:", a.id, a.name)

# ── Read ──────────────────────────────────────────────────────────────────────

asset = client.assets.get(media.id)
print("Get:", asset.id, asset.name)

# --- Filter — single page (manual cursor control) ---
page = client.assets.filter(HUB_PROFILE_ID, page_size=20, types=["Media"])
for a in page.items:
    print("Filter:", a.name, a.type)

if page.cursor:
    page2 = client.assets.filter(HUB_PROFILE_ID, page_size=20, cursor=page.cursor)

# --- Filter — iterate all pages automatically ---
for a in client.assets.filter_all(HUB_PROFILE_ID, types=["Media"]):
    print("All:", a.name, a.type)

# --- Search — returns all results in a single request ---
for a in client.assets.search_all(HUB_PROFILE_ID, search="intro", types=["Media"]):
    print("Search:", a.name, a.status)

# ── Update ────────────────────────────────────────────────────────────────────

# --- Rename only ---
updated = client.assets.update(media.id, name="Intro Video (Final)")
print("Updated:", updated.id)

# --- Rename + update cover (auto-upload) ---
updated = client.assets.update(
    media.id,
    name="Intro Video (Final)",
    cover_image="/path/to/thumbnail.jpg",
)
print("Updated with cover:", getattr(updated, "cover", None))

# --- Mark as read-only ---
updated = client.assets.update(file_asset.id, name="Employee Handbook", read_only=True)
print("Marked read-only:", updated.id)
