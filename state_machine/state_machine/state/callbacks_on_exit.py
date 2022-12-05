"""При выходе из состояния."""

import asyncio
from typing import Self

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..states_enum import StatesEnum
from .callbacks_base import CallbacksBase, TCollection


class CallbacksOnExit(CallbacksBase):
    """При выходе из состояния."""

    def __init__(
        self,
        callbacks: TCollection | None,
        name: StatesEnum,
        timeout: float | None,
        timeout_to_state: StatesEnum | None,
    ) -> None:
        """При выходе из состояния."""
        self.__new_state_data: NewStateData | None

        super().__init__(callbacks, name, timeout, timeout_to_state)
        self.__new_state_data = None

    def set_new_state_data(  # noqa: WPS615
        self,
        new_state_data: NewStateData,
    ) -> Self:
        """Задать данные нового состояния."""
        self.__new_state_data = new_state_data
        return self

    async def _run(self) -> None:
        """Запуск."""
        if self.__new_state_data is None:
            raise StateMachineError(
                "call {0} before run".format(self.set_new_state_data.__name__),
            )
        async with asyncio.TaskGroup() as tg:
            self._create_tasks(tg)
        raise NewStateException.reraise(
            new_state_data=self.__new_state_data,
            active_state=self._name,
        )

    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        if self._callbacks is None:
            return
        for task in self._callbacks:
            tg.create_task(task())

    def _except_timeout(self) -> None:
        raise NotImplementedError
