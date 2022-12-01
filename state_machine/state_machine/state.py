"""Базовый класс для состояния."""

import asyncio
from typing import Any, Callable, Coroutine

from .exceptions import (
    NewStateException,
    NewStateExceptionData,
    StateMachineError,
)
from .states_enum import StatesEnum
from .state_run_callbacks import TCollection, StateOnEnter, StateOnExit


def infinite_run_class_method(
    func: Callable[[Any], Any],
) -> Callable[[Any], Any]:
    """Бесконечный запуск для метода в классе."""

    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
        while True:  # noqa: WPS328
            return await func(self, *args, **kwargs)

    return wrapper


async def make_coro_infinite(
    coro_func: Callable[[], Coroutine[None, None, None]],
) -> None:
    """Сделать корутину бесконечно вызываемой."""
    while True:  # noqa: WPS457
        await coro_func()


class State(object):
    """Базовый класс для состояния."""

    def __init__(
        self,
        enum_value: StatesEnum,
        on_run: TCollection,
        on_enter: TCollection | None = None,
        on_exit: TCollection | None = None,
    ) -> None:
        self.__enum_value: StatesEnum
        self.__on_enter: StateOnEnter
        self.__on_run: TCollection
        self.__on_exit: StateOnExit
        self.__new_state_data: NewStateExceptionData

        self.__enum_value = enum_value
        self.__on_enter = StateOnEnter(on_enter)
        self.__on_run = on_run
        self.__on_exit = StateOnExit(on_exit)

    @property
    def enum_value(self) -> StatesEnum:
        return self.__enum_value

    async def task(self) -> None:
        print("state {0}".format(self.__enum_value))
        await self.__on_enter.run()
        await self.__task_on_run()
        await self.__on_exit.run()

    async def __task_on_run(self) -> None:
        try:
            async with asyncio.TaskGroup() as tg:
                [
                    tg.create_task(make_coro_infinite(task))
                    for task in self.__on_run
                ]
        except* NewStateException as exc:
            new_state_data = exc.exceptions
            if isinstance(new_state_data[0], NewStateException):
                self.__new_state_data = new_state_data[0].exception_data
        raise StateMachineError

    async def __task_on_exit(self) -> None:
        if self.__on_exit is None:
            return
        async with asyncio.TaskGroup() as tg:
            [tg.create_task(task()) for task in self.__on_exit]
        raise NewStateException.reraise(
            exc_data=self.__new_state_data,
            active_state=self.__enum_value,
        )
