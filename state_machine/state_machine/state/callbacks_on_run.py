"""При нахождении в состоянии."""

import asyncio
import logging
from typing import Callable, Coroutine

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..states_enum import StatesEnum
from .callbacks_base import CallbacksBase, TCollection

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


async def make_coro_infinite(
    coro_func: Callable[[], Coroutine[None, None, None]],
) -> None:
    """Сделать корутину бесконечно вызываемой."""
    while True:
        await coro_func()
        await asyncio.sleep(0)


class CallbacksOnRun(CallbacksBase):
    """При нахождении в состоянии."""

    def __init__(
        self,
        callbacks: TCollection | None,
        name: StatesEnum,
        timeout: float | None,
        timeout_to_state: StatesEnum | None,
    ) -> None:
        """При входе в состояние."""
        self.__new_state_data: NewStateData | None

        super().__init__(callbacks, name, timeout, timeout_to_state)
        self.__new_state_data = None

    async def _run(self) -> None:
        """Запуск."""
        try:
            async with asyncio.TaskGroup() as tg:
                self._create_tasks(tg)
            raise StateMachineError(
                "all run tasks complete without NewStateException",
            )
        except* NewStateException as exc:
            new_state_data = exc.exceptions
        if isinstance(new_state_data[0], NewStateException):
            self.__new_state_data = new_state_data[0].exception_data

    @property
    def new_state_data(self) -> NewStateData:
        """Данные нового состояния."""
        if self.__new_state_data is None:
            raise StateMachineError("unknown new_state_data")
        return self.__new_state_data

    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        if self._callbacks is None:
            raise StateMachineError("no tasks in on_run")
        for task in self._callbacks:
            tg.create_task(make_coro_infinite(task))

    def _except_timeout(self) -> None:
        raise NotImplementedError
