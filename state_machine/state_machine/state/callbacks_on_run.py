"""При нахождении в состоянии."""

import asyncio
from typing import Callable, Coroutine

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..states_enum import StatesEnum
from .callbacks_base import CallbacksBase, TCollection


async def make_coro_infinite(
    coro_func: Callable[[], Coroutine[None, None, None]],
) -> None:
    """Сделать корутину бесконечно вызываемой."""
    while True:  # noqa: WPS457
        await coro_func()


class CallbacksOnRun(CallbacksBase):
    """При нахождении в состоянии."""

    def __init__(
        self,
        callbacks: TCollection | None,
        name: StatesEnum,
    ) -> None:
        """При входе в состояние."""
        self.__new_state_data: NewStateData | None

        super().__init__(callbacks, name)
        self.__new_state_data = None

    async def run(self) -> None:
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
