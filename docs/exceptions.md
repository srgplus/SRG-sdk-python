<a id="srg.exceptions"></a>

# srg.exceptions

<a id="srg.exceptions.SRGError"></a>

## SRGError Objects

```python
class SRGError(Exception)
```

Base exception for all SRG SDK errors.

<a id="srg.exceptions.BadRequestError"></a>

## BadRequestError Objects

```python
class BadRequestError(APIStatusError)
```

400 Bad Request.

<a id="srg.exceptions.AuthenticationError"></a>

## AuthenticationError Objects

```python
class AuthenticationError(APIStatusError)
```

401 Unauthorized.

<a id="srg.exceptions.ForbiddenError"></a>

## ForbiddenError Objects

```python
class ForbiddenError(APIStatusError)
```

403 Forbidden.

<a id="srg.exceptions.NotFoundError"></a>

## NotFoundError Objects

```python
class NotFoundError(APIStatusError)
```

404 Not Found.

<a id="srg.exceptions.ConflictError"></a>

## ConflictError Objects

```python
class ConflictError(APIStatusError)
```

409 Conflict.

<a id="srg.exceptions.UnprocessableEntityError"></a>

## UnprocessableEntityError Objects

```python
class UnprocessableEntityError(APIStatusError)
```

422 Unprocessable Entity.

<a id="srg.exceptions.ServerError"></a>

## ServerError Objects

```python
class ServerError(APIStatusError)
```

5xx Server Error.

