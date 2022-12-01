"""Запуск функций из определения State."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Iterable

from .exceptions import NewStateException, NewStateExceptionData

TCollection = Iterable[Callable[[], Coroutine[None, None, None]]]


class _Base(ABC):
    @abstractmethod
    async def run(self, *args: Any) -> Any:
        """Запуск."""


class StateOnEnter(_Base):
    """При входе в состояние."""

    def __init__(self, callbacks: TCollection | None) -> None:
        """При входе в состояние."""
        self.__callbacks: TCollection | None

        self.__callbacks = callbacks

    async def run(self) -> None:
        """Запуск."""
        if self.__callbacks is None:
            return
        async with asyncio.TaskGroup() as tg:
            [tg.create_task(task()) for task in self.__callbacks]


class StateOnExit(_Base):
    """При выходе из состояния."""

    def __init__(self, callbacks: TCollection | None) -> None:
        """При выходе из состояния."""
        self.__callbacks: TCollection | None

        self.__callbacks = callbacks

    async def run(self, new_state_data: NewStateExceptionData) -> None:
        """Запуск."""
        if self.__callbacks is None:
            return
        async with asyncio.TaskGroup() as tg:
            [tg.create_task(task()) for task in self.__callbacks]
        raise NewStateException.reraise(
            exc_data=new_state_data,
            active_state=self.__enum_value,
        )
