import httpx


class SRGError(Exception):
    """Base exception for all SRG SDK errors."""

    def __init__(
        self,
        message: str = "SRG API error.",
        body: object = None,
        response: httpx.Response | None = None,
    ) -> None:
        self.message = message
        self.body = body
        self.response = response
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message!r})"


class APIStatusError(SRGError):
    status_code: int

    def __init__(self, body: object, response: httpx.Response) -> None:
        status = response.status_code
        detail = _extract_detail(body)
        super().__init__(f"HTTP {status}{detail}", body=body, response=response)
        self.status_code = status


class BadRequestError(APIStatusError):
    """400 Bad Request."""


class AuthenticationError(APIStatusError):
    """401 Unauthorized."""


class ForbiddenError(APIStatusError):
    """403 Forbidden."""


class NotFoundError(APIStatusError):
    """404 Not Found."""


class ConflictError(APIStatusError):
    """409 Conflict."""


class UnprocessableEntityError(APIStatusError):
    """422 Unprocessable Entity."""


class ServerError(APIStatusError):
    """5xx Server Error."""


def _extract_detail(body: object) -> str:
    if isinstance(body, dict):
        if body.get("detail"):
            return f": {body['detail']}"
        # ASP.NET ProblemDetails / FluentValidation put per-field messages in
        # `errors` ({field: [msgs]}). Surface them so a caller (e.g. an agent
        # writing widgets) sees WHICH field was rejected instead of a bare 400
        # and having to bisect. Fall back to the generic `title` otherwise.
        errors = body.get("errors")
        if isinstance(errors, dict) and errors:
            parts = []
            for field, msgs in errors.items():
                text = "; ".join(str(m) for m in msgs) if isinstance(msgs, list) else str(msgs)
                parts.append(f"{field}: {text}" if field else text)
            return ": " + " | ".join(parts)
        if body.get("title"):
            return f": {body['title']}"
    if isinstance(body, str) and body:
        return f": {body}"
    return ""
