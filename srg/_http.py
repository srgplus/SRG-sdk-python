# flake8: noqa: ANN401

import contextvars
from typing import Any

import httpx

from srg.exceptions import (
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    SRGError,
    UnprocessableEntityError,
)

# Context variable that carries the active workspace API key for the current
# call stack / async task. ``with_api_key`` and ``use_api_key`` set this; the
# HTTP client reads it on every request and injects ``Authorization`` per call.
_active_api_key: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "srg_active_api_key", default=None
)


def _get_active_api_key(default: str | None) -> str:
    """Return the api key bound to this context, or the client's default.

    Raises ``SRGError`` if neither is set.
    """
    key = _active_api_key.get()
    if key is None:
        key = default
    if not key:
        raise SRGError(
            "No api_key bound. Call client.with_api_key() or use_api_key()."
        )
    return key


class BaseHTTPClient:
    def __init__(self, *, api_key: str | None, base_url: str, timeout: float) -> None:
        # ``api_key`` is the *default* key when nothing is bound via the
        # context manager / scoped clone. When ``None`` the caller MUST bind a
        # key per-request, otherwise the request will raise ``SRGError``.
        self._default_api_key = api_key or None
        self._base_url = base_url
        self._timeout = timeout

    @staticmethod
    def _base_headers() -> dict[str, str]:
        """Static headers baked into the underlying httpx client."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _auth_headers(self) -> dict[str, str]:
        """Per-request headers — resolves the active api key from context."""
        return {"Authorization": f"Bearer {_get_active_api_key(self._default_api_key)}"}

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        try:
            body: object = response.json()
        except Exception:
            body = response.text or None

        code = response.status_code
        if code == 400:
            raise BadRequestError(body, response)
        if code == 401:
            raise AuthenticationError(body, response)
        if code == 403:
            raise ForbiddenError(body, response)
        if code == 404:
            raise NotFoundError(body, response)
        if code == 409:
            raise ConflictError(body, response)
        if code == 422:
            raise UnprocessableEntityError(body, response)
        if code >= 500:
            raise ServerError(body, response)
        raise APIStatusError(body, response)

    def _process(self, response: httpx.Response) -> Any:
        self._raise_for_status(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()


class SyncHTTPClient(BaseHTTPClient):
    def __init__(
        self, *, api_key: str | None, base_url: str, timeout: float
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=self._base_headers(),
            timeout=self._timeout,
        )

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._process(
            self._client.get(path, params=params, headers=self._auth_headers())
        )

    def post(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(
            self._client.post(
                path, json=json, params=params, headers=self._auth_headers()
            )
        )

    def put(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(
            self._client.put(
                path, json=json, params=params, headers=self._auth_headers()
            )
        )

    def patch(self, path: str, *, json: Any = None) -> Any:
        return self._process(
            self._client.patch(path, json=json, headers=self._auth_headers())
        )

    def delete(self, path: str) -> Any:
        return self._process(
            self._client.delete(path, headers=self._auth_headers())
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SyncHTTPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncHTTPClient(BaseHTTPClient):
    def __init__(
        self, *, api_key: str | None, base_url: str, timeout: float
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._base_headers(),
            timeout=self._timeout,
        )

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._process(
            await self._client.get(
                path, params=params, headers=self._auth_headers()
            )
        )

    async def post(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(
            await self._client.post(
                path, json=json, params=params, headers=self._auth_headers()
            )
        )

    async def put(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(
            await self._client.put(
                path, json=json, params=params, headers=self._auth_headers()
            )
        )

    async def patch(self, path: str, *, json: Any = None) -> Any:
        return self._process(
            await self._client.patch(
                path, json=json, headers=self._auth_headers()
            )
        )

    async def delete(self, path: str) -> Any:
        return self._process(
            await self._client.delete(path, headers=self._auth_headers())
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncHTTPClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
