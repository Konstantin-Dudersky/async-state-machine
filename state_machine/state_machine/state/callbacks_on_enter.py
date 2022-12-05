"""При входе в состояние."""

import asyncio

from .callbacks_base import CallbacksBase
from ..exceptions import StateTimeoutError


class CallbacksOnEnter(CallbacksBase):
    """При входе в состояние."""

    async def _run(self) -> None:
        """Запуск."""
        async with asyncio.TaskGroup() as tg:
            self._create_tasks(tg)

    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        if self._callbacks is None:
            return
        for task in self._callbacks:
            tg.create_task(task())

    def _except_timeout(self) -> None:
        if self._timeout_to_state is None:
            raise StateTimeoutError
