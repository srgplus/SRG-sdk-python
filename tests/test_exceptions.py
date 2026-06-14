"""_extract_detail: how an HTTP error body becomes the message tail.

The validation branch matters for write tools: ASP.NET ProblemDetails /
FluentValidation return per-field messages under `errors`, and surfacing them
turns a bare "HTTP 400" into "HTTP 400: AssetId: required" so a caller can
self-correct instead of bisecting one widget at a time.
"""

from __future__ import annotations

from srg.exceptions import _extract_detail


def test_detail_is_preferred():
    assert _extract_detail({"detail": "boom"}) == ": boom"


def test_validation_errors_are_surfaced_over_generic_title():
    body = {
        "title": "One or more validation errors occurred.",
        "status": 400,
        "errors": {"AssetId": ["The AssetId field is required."]},
    }
    out = _extract_detail(body)
    assert "AssetId" in out and "required" in out
    assert "validation errors occurred" not in out  # generic title suppressed


def test_multiple_fields_joined():
    body = {"errors": {"AssetId": ["required"], "Title": ["too long"]}}
    out = _extract_detail(body)
    assert "AssetId: required" in out
    assert "Title: too long" in out
    assert "|" in out


def test_title_used_when_no_errors():
    assert _extract_detail({"title": "Bad Request"}) == ": Bad Request"


def test_empty_errors_falls_back_to_title():
    assert _extract_detail({"title": "Bad Request", "errors": {}}) == ": Bad Request"


def test_string_body():
    assert _extract_detail("oops") == ": oops"


def test_no_detail():
    assert _extract_detail({}) == ""
    assert _extract_detail(None) == ""
