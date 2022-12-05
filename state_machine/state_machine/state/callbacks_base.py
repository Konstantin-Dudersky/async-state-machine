"""Запуск функций из определения State."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Final, Iterable, Literal

from ..states_enum import StatesEnum
from ..exceptions import NewStateData, NewStateException, StateMachineError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TCollection = Iterable[Callable[[], Coroutine[None, None, None]]]


EXC_TIMEOUT: Final[str] = "Timeout occur in state {name}, stage {stage}"
EXC_TIMEOUT_WITHOUT_TARGET: Final[
    str
] = "{base_msg}, but target state not specified"


class Callbacks(object):
    """Класс для запуска задач."""

    def __init__(
        self,
        callbacks: TCollection | None,
        timeout: float | None,
        timeout_to_state: StatesEnum | None,
        name: StatesEnum,
        stage: Literal["on_enter", "on_run", "on_exit"],
    ) -> None:
        """Класс для запуска задач."""
        self.__callbacks: TCollection | None
        self.__name: StatesEnum
        self.__timeout: float | None
        self.__timeout_to_state: StatesEnum | None
        self.__stage: str

        self.__callbacks = callbacks
        self.__name = name
        self.__timeout = timeout
        self.__timeout_to_state = timeout_to_state
        self.__stage = stage

    async def run(self) -> None:
        """Запуск."""
        log.debug(
            "Start run state {name}, stage {stage}".format(
                name=self.__name,
                stage=self.__stage,
            )
        )
        new_state_data: NewStateData | None = None
        try:
            await self.__run_with_timeout()
        except* asyncio.TimeoutError:
            self._except_timeout()
        except* NewStateException as exc:
            new_state_data = self._except_new_state(exc)
        if new_state_data is not None:
            raise NewStateException.reraise(new_state_data, self.__name)

    async def __run_with_timeout(self) -> None:
        if self.__timeout is None:
            await self._create_taskgroup()
            return
        async with asyncio.timeout(self.__timeout):
            await self._create_taskgroup()

    async def _create_taskgroup(self) -> None:
        """Запуск."""
        async with asyncio.TaskGroup() as tg:
            self._create_tasks(tg)

    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        """Создание группы задач."""
        if self.__callbacks is None:
            return
        for task in self.__callbacks:
            tg.create_task(task())

    def _except_timeout(self) -> None:
        """Обработка превышения времени выполнения."""
        log.debug(EXC_TIMEOUT.format(name=self.__name, stage=self.__stage))
        if self.__timeout_to_state is None:
            msg = EXC_TIMEOUT_WITHOUT_TARGET.format(
                base_msg=EXC_TIMEOUT.format(
                    name=self.__name,
                    stage=self.__stage,
                )
            )
            log.error(msg)
            raise StateMachineError(msg)
        raise NewStateException(
            new_state=self.__timeout_to_state,
        )

    def _except_new_state(
        self,
        exc: ExceptionGroup[NewStateException],
    ) -> NewStateData:
        """Обработка перехода в новое состояние."""
        new_state_data = exc.exceptions[0]
        if isinstance(new_state_data, NewStateException):
            return new_state_data.exception_data
        raise StateMachineError


class CallbacksBase(ABC):
    """Абстрактный класс для запуска задач."""

    def __init__(
        self,
        callbacks: TCollection | None,
        name: StatesEnum,
        timeout: float | None,
        timeout_to_state: StatesEnum | None,
    ) -> None:
        """Абстрактный класс для запуска задач."""
        self._callbacks: TCollection | None
        self._name: StatesEnum
        self.__timeout: float | None
        self._timeout_to_state: StatesEnum | None

        self._callbacks = callbacks
        self._name = name
        self._timeout_to_state = timeout_to_state
        self.__timeout = timeout

    async def run(self) -> None:
        """Запуск."""
        try:
            await self.__run_with_timeout()
        except asyncio.TimeoutError:
            log.debug(EXC_TIMEOUT.format(name=self._name))
            self._except_timeout()

    @abstractmethod
    async def _run(self) -> None:
        """Запуск."""

    @abstractmethod
    def _create_tasks(self, tg: asyncio.TaskGroup) -> None:
        """Создание группы задач."""

    @abstractmethod
    def _except_timeout(self) -> None:
        """Обработка превышения времени выполнения."""

    async def __run_with_timeout(self) -> None:
        if self.__timeout is None:
            await self._run()
        else:
            async with asyncio.timeout(1.0):
                await self._run()
