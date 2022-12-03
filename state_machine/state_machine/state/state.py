"""Состояние."""

from typing import Any, Callable

from ..states_enum import StatesEnum
from .callbacks_base import TCollection
from .callbacks_on_enter import CallbacksOnEnter
from .callbacks_on_exit import CallbacksOnExit
from .callbacks_on_run import CallbacksOnRun


def infinite_run_class_method(
    func: Callable[[Any], Any],
) -> Callable[[Any], Any]:
    """Бесконечный запуск для метода в классе."""

    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
        while True:  # noqa: WPS328
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
    ) -> None:
        """Состояние."""
        self.__name: StatesEnum
        self.__on_enter: CallbacksOnEnter
        self.__on_run: CallbacksOnRun
        self.__on_exit: CallbacksOnExit

        self.__name = name
        self.__on_enter = CallbacksOnEnter(on_enter, self.__name)
        self.__on_run = CallbacksOnRun(on_run, self.__name)
        self.__on_exit = CallbacksOnExit(on_exit, self.__name)

    @property
    def name(self) -> StatesEnum:
        """Имя состояния."""
        return self.__name

    async def task(self) -> None:
        """Задача для асинхронного выполнения, вызывается из StateMachine."""
        print("state {0}".format(self.__name))
        await self.__on_enter.run()
        await self.__on_run.run()
        await self.__on_exit.set_new_state_data(
            self.__on_run.new_state_data,
        ).run()
