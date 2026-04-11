from srg.schemas.common import CursorPagedList, async_paginate, paginate
from srg.schemas.content import ContentSearch


def _make_page(names: list[str], cursor: str | None) -> CursorPagedList[ContentSearch]:
    items = [ContentSearch(id=str(i), name=n) for i, n in enumerate(names)]
    return CursorPagedList[ContentSearch](items=items, cursor=cursor)


class TestPaginate:
    def test_single_page(self) -> None:
        page = _make_page(["A", "B"], cursor=None)
        results = list(paginate(lambda _: page))
        assert [r.name for r in results] == ["A", "B"]

    def test_multiple_pages(self) -> None:
        pages = [
            _make_page(["A", "B"], cursor="page2"),
            _make_page(["C"], cursor=None),
        ]
        it = iter(pages)
        results = list(paginate(lambda _: next(it)))
        assert [r.name for r in results] == ["A", "B", "C"]

    def test_empty_page(self) -> None:
        page = _make_page([], cursor=None)
        results = list(paginate(lambda _: page))
        assert results == []

    def test_cursor_passed_to_fetch(self) -> None:
        cursors_received: list[str | None] = []

        def fetch(cursor: str | None) -> CursorPagedList[ContentSearch]:
            cursors_received.append(cursor)
            if cursor is None:
                return _make_page(["A"], cursor="next")
            return _make_page(["B"], cursor=None)

        list(paginate(fetch))
        assert cursors_received == [None, "next"]


class TestAsyncPaginate:
    async def test_single_page(self) -> None:
        page = _make_page(["A", "B"], cursor=None)

        async def fetch(cursor: str | None) -> CursorPagedList[ContentSearch]:
            return page

        results = [item async for item in async_paginate(fetch)]
        assert [r.name for r in results] == ["A", "B"]

    async def test_multiple_pages(self) -> None:
        pages = [
            _make_page(["A", "B"], cursor="page2"),
            _make_page(["C"], cursor=None),
        ]
        it = iter(pages)

        async def fetch(cursor: str | None) -> CursorPagedList[ContentSearch]:
            return next(it)

        results = [item async for item in async_paginate(fetch)]
        assert [r.name for r in results] == ["A", "B", "C"]

    async def test_cursor_passed_to_fetch(self) -> None:
        cursors_received: list[str | None] = []

        async def fetch(cursor: str | None) -> CursorPagedList[ContentSearch]:
            cursors_received.append(cursor)
            if cursor is None:
                return _make_page(["A"], cursor="next")
            return _make_page(["B"], cursor=None)

        [item async for item in async_paginate(fetch)]
        assert cursors_received == [None, "next"]
