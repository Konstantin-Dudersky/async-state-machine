"""При входе в состояние."""

import asyncio

from .callbacks_base import CallbacksBase


class CallbacksOnEnter(CallbacksBase):
    """При входе в состояние."""

    async def run(self) -> None:
        """Запуск."""
        async with asyncio.TaskGroup() as tg:
            self._create_tasks(tg)

    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        if self._callbacks is None:
            return
        for task in self._callbacks:
            tg.create_task(task())
