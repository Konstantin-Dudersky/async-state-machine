"""Состояние."""

import asyncio
from typing import Any, Callable, Final

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..states_enum import StatesEnum
from .callbacks_base import TCollection, Callbacks


EXC_NO_ON_RUN: Final[str] = "No callbacks on on_run input, state: {name}"


def infinite_run_class_method(
    func: Callable[[Any], Any],
) -> Callable[[Any], Any]:
    """Бесконечный запуск для метода в классе."""

    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
        while True:  # noqa: WPS328
            await asyncio.sleep(0)
            return await func(self, *args, **kwargs)

    return wrapper


class State(object):
    """Состояние."""

    def __init__(
        self,
        name: StatesEnum,
        on_run: TCollection,
        on_enter: TCollection | None = None,
        on_exit: TCollection | None = None,
        timeout_on_enter: float | None = 2.0,
        timeout_on_enter_to_state: StatesEnum | None = None,
        timeout_on_run: float | None = None,
        timeout_on_run_to_state: StatesEnum | None = None,
        timeout_on_exit: float | None = 2.0,
        timeout_on_exit_to_state: StatesEnum | None = None,
    ) -> None:
        """Состояние.

        Parameters
        ----------
        timeout_on_enter
            Ограничение времени on_run. None - без ограничения.
        """
        self.__name: StatesEnum
        self.__on_enter: Callbacks
        self.__on_run: Callbacks
        self.__on_exit: Callbacks
        self.__new_state_data: NewStateData | None

        if not on_run:
            raise StateMachineError(EXC_NO_ON_RUN.format(name=name))
        self.__name = name
        self.__on_enter = Callbacks(
            callbacks=on_enter,
            timeout=timeout_on_enter,
            timeout_to_state=timeout_on_enter_to_state,
            name=self.__name,
            stage="on_enter",
        )
        self.__on_run = Callbacks(
            callbacks=on_run,
            timeout=timeout_on_run,
            timeout_to_state=timeout_on_run_to_state,
            name=self.__name,
            stage="on_run",
        )
        self.__on_exit = Callbacks(
            callbacks=on_exit,
            timeout=timeout_on_exit,
            timeout_to_state=timeout_on_exit_to_state,
            name=self.__name,
            stage="on_exit",
        )
        self.__new_state_data = None

    @property
    def name(self) -> StatesEnum:
        """Имя состояния."""
        return self.__name

    async def run(self) -> None:
        """Задача для асинхронного выполнения, вызывается из StateMachine."""
        await self.__run_on_enter()
        await self.__run_on_run()
        await asyncio.sleep(1)
        await self.__run_on_exit()
        if self.__new_state_data is None:
            raise StateMachineError
        raise NewStateException.reraise(
            new_state_data=self.__new_state_data,
            active_state=self.__name,
        )

    async def __run_on_enter(self) -> None:
        try:
            await self.__on_enter.run()
        except NewStateException as exc:
            self.__new_state_data = exc.exception_data

    async def __run_on_run(self) -> None:
        if self.__new_state_data is not None:
            return
        try:
            await self.__on_run.run()
        except NewStateException as exc:
            self.__new_state_data = exc.exception_data

    async def __run_on_exit(self) -> None:
        try:
            await self.__on_exit.run()
        except NewStateException as exc:
            self.__new_state_data = exc.exception_data
