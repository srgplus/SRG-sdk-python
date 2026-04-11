# flake8: noqa: T201
"""
Media uploads — avatar, cover and content file examples.

Every resource that accepts images supports two modes:

  Auto-upload  — pass a local file path or an http(s):// URL.
                 The SDK fetches/reads the file, requests a signed S3 URL
                 from the API, uploads directly to S3, then returns the
                 fully-populated object with the image already set.

  Manual mode  — pass the extension / FileUploadParameters object.
                 The API returns a signed URL that you can upload to
                 yourself (e.g. from a browser or a different server).
"""

from srg import SRGClient
from srg.schemas.asset import MediaAssetCreate
from srg.schemas.common import (
    ContentFileUploadParameters,
    FileUploadParameters,
    ImageUpsert,
)

client = SRGClient(api_key="SRG_API_KEY")

WORKSPACE_ID = "your-workspace-id"
HUB_PROFILE_ID = "your-hub-profile-id"

# ═══════════════════════════════════════════════════════════════════════════════
# Hub Profile — avatar & cover
# ═══════════════════════════════════════════════════════════════════════════════

# --- Create with avatar from local file ---
profile = client.hub_profiles.create(
    name="Demo Hub",
    user_name="demo-hub",
    avatar_image="/path/to/avatar.png",
    workspace_id=WORKSPACE_ID,
)
print("Avatar url:", profile.avatar.details.url if profile.avatar else None)

# --- Create with avatar from URL (SDK downloads & re-uploads) ---
profile = client.hub_profiles.create(
    name="Remote Hub",
    user_name="remote-hub",
    avatar_image="https://example.com/avatar.jpg",
    cover_image="https://example.com/cover.jpg",
    workspace_id=WORKSPACE_ID,
)
print("Cover url:", profile.cover.details.url if profile.cover else None)

# --- Create — manual mode (get signed URLs, upload yourself) ---
result = client.hub_profiles.create(
    name="Manual Hub",
    user_name="manual-hub",
    avatar_extension="jpg",
    cover_extension="png",
    workspace_id=WORKSPACE_ID,
)
# result is HubProfileSignedUrls
if result.avatar_signed_url:
    print("Upload avatar to:", result.avatar_signed_url.url)
if result.cover_signed_url:
    print("Upload cover to:", result.cover_signed_url.url)

# --- Update hub profile avatar (auto-upload) ---
profile = client.hub_profiles.update(
    HUB_PROFILE_ID,
    name="Demo Hub",
    user_name="demo-hub",
    avatar_image="/path/to/new_avatar.jpg",
)
print("Updated avatar:", profile.avatar)

# --- Update hub profile cover only (auto-upload) ---
profile = client.hub_profiles.update(
    HUB_PROFILE_ID,
    name="Demo Hub",
    user_name="demo-hub",
    cover_image="/path/to/cover.png",
)
print("Updated cover:", profile.cover)

# --- Update — manual mode ---
result = client.hub_profiles.update(
    HUB_PROFILE_ID,
    name="Demo Hub",
    user_name="demo-hub",
    avatar=FileUploadParameters(extension="jpg", generate_signed_url=True),
)
# result is HubProfileSignedUrls
if result.avatar_signed_url:
    print("Manual upload avatar to:", result.avatar_signed_url.url)

# ═══════════════════════════════════════════════════════════════════════════════
# Content — cover image
# ═══════════════════════════════════════════════════════════════════════════════

# --- Create content with cover (auto-upload from file) ---
content = client.contents.create(
    name="Video Tutorial",
    hub_profile_id=HUB_PROFILE_ID,
    cover_image="/path/to/cover.jpg",
)
print("Content cover:", content.cover.urls.original if content.cover else None)

# --- Create content with cover from URL ---
content = client.contents.create(
    name="Remote Cover Tutorial",
    hub_profile_id=HUB_PROFILE_ID,
    cover_image="https://example.com/thumbnail.jpg",
)
print("Content cover from URL:", content.cover)

# --- Create content — manual mode ---
result = client.contents.create(
    name="Manual Cover Tutorial",
    hub_profile_id=HUB_PROFILE_ID,
    cover=ImageUpsert(width=1920, height=1080, size=204_800, extension="jpg"),
)
# result is ContentUploadSignedUrl
if result.cover_signed_url:
    print("Upload content cover to:", result.cover_signed_url.url)
    print("Extra headers (required for S3):", result.metadata_headers)

# --- Update content cover (auto-upload) ---
content = client.contents.update(
    result.id,
    name="Manual Cover Tutorial",
    hub_profile_id=HUB_PROFILE_ID,
    cover_image="/path/to/new_cover.jpg",
)
print("Updated content cover:", content.cover)

# --- Update content cover — manual mode ---
upd_result = client.contents.update(
    result.id,
    name="Manual Cover Tutorial",
    hub_profile_id=HUB_PROFILE_ID,
    cover=ContentFileUploadParameters(generate_signed_url=True),
)
if upd_result.cover_signed_url:
    print("Manual update cover URL:", upd_result.cover_signed_url.url)

# ═══════════════════════════════════════════════════════════════════════════════
# Asset — cover image (thumbnail)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Create a media asset first ---
media = client.assets.create(
    hub_profile_id=HUB_PROFILE_ID,
    asset=MediaAssetCreate(
        name="Product Demo",
        duration_in_seconds=300.0,
        memory_size_in_bytes=157_286_400,
    ),
)

# --- Update asset with cover (auto-upload from file) ---
updated_media = client.assets.update(
    media.id,
    name="Product Demo",
    cover_image="/path/to/thumbnail.jpg",
)
print("Asset cover:", updated_media.cover if hasattr(updated_media, "cover") else None)

# --- Update asset cover from URL ---
updated_media = client.assets.update(
    media.id,
    name="Product Demo",
    cover_image="https://example.com/thumb.jpg",
)
print("Asset cover from URL:", updated_media)

# --- Update asset cover — manual mode ---
result_asset = client.assets.update(
    media.id,
    name="Product Demo",
    cover=ContentFileUploadParameters(generate_signed_url=True),
)
# result_asset is AssetUploadSignedUrl
if result_asset.cover_signed_url:
    print("Upload asset cover to:", result_asset.cover_signed_url.url)
    print("Extra headers:", result_asset.metadata_headers)

# ═══════════════════════════════════════════════════════════════════════════════
# Workspace — cover image
# ═══════════════════════════════════════════════════════════════════════════════

# --- Update workspace cover (auto-upload from file) ---
workspace = client.workspaces.update(
    WORKSPACE_ID,
    name="Acme Corp",
    cover_image="/path/to/workspace_cover.jpg",
)
print("Workspace cover:", workspace.cover)

# --- Update workspace cover from URL ---
workspace = client.workspaces.update(
    WORKSPACE_ID,
    name="Acme Corp",
    cover_image="https://example.com/workspace_bg.png",
)
print("Workspace cover from URL:", workspace.cover)

# --- Update workspace cover — manual mode ---
result_ws = client.workspaces.update(
    WORKSPACE_ID,
    name="Acme Corp",
    cover=FileUploadParameters(extension="jpg", generate_signed_url=True),
)
# result_ws is WorkspaceSignedUrl
if result_ws.cover_signed_url:
    print("Upload workspace cover to:", result_ws.cover_signed_url.url)
