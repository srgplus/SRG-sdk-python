# flake8: noqa: T201
"""
Assets — upload / read / search / filter / update examples.

Recommended API:
  upload()        — create + upload a single file in one call.
  upload_batch()  — create + upload multiple files in a single batched flow.

Both auto-detect the asset kind from the file extension:
  • Image  — png, jpg, jpeg, gif, bmp, webp, heic, svg
  • Video  — mp4, mov, mkv, webm, avi, …
  • File   — anything else (pdf, zip, txt, …)

For images the SDK reads width/height directly from the file header (PNG,
JPEG, GIF, BMP, WEBP) — no extra dependency. Pillow is used as a fallback
for HEIC and other formats; you can also pass ``width=``/``height=``
explicitly.

Embeds (YouTube, Vimeo, …) and the legacy "Media" type still go through
:meth:`AssetsResource.create`, which is kept for that use case.
"""

from srg import SRGClient
from srg.resources.assets import AssetUploadInput
from srg.schemas.asset import EmbedAssetCreate

client = SRGClient(api_key="SRG_API_KEY")

HUB_PROFILE_ID = "your-hub-profile-id"

# ── Upload (single) ───────────────────────────────────────────────────────────

# --- Image — kind, width, and height auto-detected from the file header ---
image = client.assets.upload(
    hub_profile_id=HUB_PROFILE_ID,
    file="/path/to/banner.png",
)
print("Uploaded image:", image.id, image.name)

# --- Video (raw upload, no transcoding pipeline) ---
video = client.assets.upload(
    hub_profile_id=HUB_PROFILE_ID,
    file="/path/to/clip.mp4",
    name="Launch Teaser",
)
print("Uploaded video:", video.id, video.name)

# --- Arbitrary file (PDF, ZIP, TXT, …) ---
doc = client.assets.upload(
    hub_profile_id=HUB_PROFILE_ID,
    file="/path/to/handbook.pdf",
    name="Employee Handbook",
)
print("Uploaded file:", doc.id, doc.name)

# --- Image with explicit width/height (e.g. for HEIC without Pillow) ---
heic = client.assets.upload(
    hub_profile_id=HUB_PROFILE_ID,
    file="/path/to/photo.heic",
    width=4032,
    height=3024,
)
print("Uploaded HEIC:", heic.id)


# --- Track upload progress (large files / multipart) ---
def show_progress(uploaded: int, total: int) -> None:
    print(f"  {uploaded / total:.0%}  ({uploaded}/{total} bytes)")


big = client.assets.upload(
    hub_profile_id=HUB_PROFILE_ID,
    file="/path/to/large_video.mp4",
    name="Conference Recording",
    on_progress=show_progress,
)
print("Uploaded big video:", big.id)

# ── Upload (batch) ────────────────────────────────────────────────────────────

# Mixed types in a single batched call. Progress is aggregated across the
# whole batch.
assets = client.assets.upload_batch(
    hub_profile_id=HUB_PROFILE_ID,
    files=[
        AssetUploadInput(file="/path/to/banner.png"),
        AssetUploadInput(file="/path/to/clip.mp4", name="Teaser"),
        AssetUploadInput(file="/path/to/handbook.pdf"),
    ],
    on_progress=show_progress,
)
for a in assets:
    print("Batch uploaded:", type(a).__name__, a.id, a.name)

# ── Embeds (YouTube / Vimeo / …) ──────────────────────────────────────────────

# Embeds don't have a file payload, so they still use the simple create()
# call (no upload step required).
embed = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=EmbedAssetCreate(
        name="Company Overview",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ),
)
print("Created embed:", embed.id)

# ── Read ──────────────────────────────────────────────────────────────────────

# --- Get one asset by id ---
asset = client.assets.get(image.id)
print("Get:", asset.id, asset.name)

# --- Filter — single page (manual cursor control) ---
page = client.assets.filter(HUB_PROFILE_ID, page_size=20, types=["Image"])
for a in page.items:
    print("Filter:", a.name, a.type)

if page.cursor:
    page2 = client.assets.filter(HUB_PROFILE_ID, page_size=20, cursor=page.cursor)

# --- Filter — iterate every page automatically ---
for a in client.assets.filter_all(HUB_PROFILE_ID, types=["Image", "Video"]):
    print("All:", a.name, a.type)

# --- Search — name/keyword match across the hub profile ---
for a in client.assets.search_all(HUB_PROFILE_ID, search="banner"):
    print("Search:", a.name, a.type)

# ── Update ────────────────────────────────────────────────────────────────────

# --- Rename only ---
updated = client.assets.update(image.id, name="Banner (Final)")
print("Renamed:", updated.id)

# --- Rename + replace cover (auto-upload from local path or URL) ---
updated = client.assets.update(
    video.id,
    name="Launch Teaser",
    cover_image="/path/to/thumbnail.jpg",
)
print("Updated with cover:", getattr(updated, "cover", None))

# --- Mark as read-only ---
updated = client.assets.update(doc.id, name="Employee Handbook", read_only=True)
print("Marked read-only:", updated.id)
