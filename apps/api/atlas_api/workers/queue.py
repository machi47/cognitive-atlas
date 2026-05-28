from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


class AsyncTaskQueue:
    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()

    def submit(self, coro_factory: Callable[[], Awaitable[Any]]) -> asyncio.Task[Any]:
        task = asyncio.create_task(coro_factory())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def drain(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

