"""Запуск функций из определения State."""

import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Iterable

from ..states_enum import StatesEnum

TCollection = Iterable[Callable[[], Coroutine[None, None, None]]]


class CallbacksBase(ABC):
    """Абстрактный класс для запуска задач."""

    def __init__(
        self,
        callbacks: TCollection | None,
        name: StatesEnum,
    ) -> None:
        """Абстрактный класс для запуска задач."""
        self._callbacks: TCollection | None
        self._name: StatesEnum

        self._callbacks = callbacks
        self._name = name

    @abstractmethod
    async def run(self) -> None:
        """Запуск."""

    @abstractmethod
    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        """Создание группы задач."""
