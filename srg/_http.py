# flake8: noqa: ANN401

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
    UnprocessableEntityError,
)


class BaseHTTPClient:
    def __init__(self, *, api_key: str, base_url: str, timeout: float) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    @staticmethod
    def _default_headers(api_key: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

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
    def __init__(self, *, api_key: str, base_url: str, timeout: float) -> None:
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=self._default_headers(api_key),
            timeout=self._timeout,
        )

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._process(self._client.get(path, params=params))

    def post(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(self._client.post(path, json=json, params=params))

    def put(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(self._client.put(path, json=json, params=params))

    def patch(self, path: str, *, json: Any = None) -> Any:
        return self._process(self._client.patch(path, json=json))

    def delete(self, path: str) -> Any:
        return self._process(self._client.delete(path))

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SyncHTTPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncHTTPClient(BaseHTTPClient):
    def __init__(self, *, api_key: str, base_url: str, timeout: float) -> None:
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._default_headers(api_key),
            timeout=self._timeout,
        )

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._process(await self._client.get(path, params=params))

    async def post(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(await self._client.post(path, json=json, params=params))

    async def put(
        self, path: str, *, json: Any = None, params: dict[str, Any] | None = None
    ) -> Any:
        return self._process(await self._client.put(path, json=json, params=params))

    async def patch(self, path: str, *, json: Any = None) -> Any:
        return self._process(await self._client.patch(path, json=json))

    async def delete(self, path: str) -> Any:
        return self._process(await self._client.delete(path))

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncHTTPClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
