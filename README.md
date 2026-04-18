# SRG+ Python SDK

Python client for the [SRG+](https://srgplus.com) API — manage hub profiles, channels, contents, assets, workspaces, and permissions.

## Installation

```bash
pip install srgplus
```

Requires Python 3.11+ and depends on `httpx` and `pydantic`.

## Quick start

```python
from srg import SRGClient

with SRGClient(api_key="srgplus_...") as client:
    profiles = client.hub_profiles.list()
    contents = client.contents.filter(profiles[0].id)
```

The `api_key` can also be provided via the `SRG_API_KEY` environment variable:

```bash
export SRG_API_KEY=srgplus_...
```

```python
client = SRGClient()  # reads from env
```

### Async

```python
import asyncio
from srg import AsyncSRGClient

async def main():
    async with AsyncSRGClient(api_key="srgplus_...") as client:
        channels = await client.channels.list(hub_profile_id="hp-id")

asyncio.run(main())
```

## Configuration

| Parameter | Env var | Default |
|-----------|---------|---------|
| `api_key` | `SRG_API_KEY` | required |
| `timeout` | — | `30.0` s |

## Documentation

Full API reference and usage examples are in [`docs/`](docs/):

| Section | Reference |
|---------|-----------|
| Client (`SRGClient`, `AsyncSRGClient`) | [docs/client.md](docs/client.md) |
| Users | [docs/resources/users.md](docs/resources/users.md) |
| Invitations | [docs/resources/invitations.md](docs/resources/invitations.md) |
| Permissions | [docs/resources/permissions.md](docs/resources/permissions.md) |
| Permission Groups | [docs/resources/permission_groups.md](docs/resources/permission_groups.md) |
| Hub Profiles | [docs/resources/hub_profiles.md](docs/resources/hub_profiles.md) |
| Workspaces | [docs/resources/workspaces.md](docs/resources/workspaces.md) |
| Assets | [docs/resources/assets.md](docs/resources/assets.md) |
| Channels | [docs/resources/channels.md](docs/resources/channels.md) |
| Contents | [docs/resources/contents.md](docs/resources/contents.md) |
| Error handling | [docs/exceptions.md](docs/exceptions.md) |

## License

MIT — see [LICENSE](LICENSE).