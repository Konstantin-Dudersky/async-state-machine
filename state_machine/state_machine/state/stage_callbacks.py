"""Запуск функций для этапа состояния."""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Final, Literal

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..states_enum import StatesEnum
from ..typings import TCallback, TCallbackCollection

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


EXC_TIMEOUT: Final[str] = "Timeout occur in state {name}, stage {stage}"
EXC_TIMEOUT_WITHOUT_TARGET: Final[
    str
] = "{base_msg}, but target state not specified"


class StageCallbacks(object):
    """Запуск функций для этапа состояния."""

    def __init__(
        self,
        callbacks: TCallbackCollection | None,
        timeout: float | None,
        timeout_to_state: StatesEnum | None,
        name: StatesEnum,
        stage: Literal["on_enter", "on_run", "on_exit"],
        coro_wrapper: Callable[[TCallback], Coroutine[Any, Any, None]],
    ) -> None:
        """Запуск функций для этапа состояния."""
        self.__callbacks: TCallbackCollection | None
        self.__coro_wrapper: Any
        self.__name: StatesEnum
        self.__timeout: float | None
        self.__timeout_to_state: StatesEnum | None
        self.__stage: str

        self.__callbacks = callbacks
        self.__coro_wrapper = coro_wrapper
        self.__name = name
        self.__stage = stage
        self.__timeout = timeout
        self.__timeout_to_state = timeout_to_state

    async def run(self) -> None:
        """Запуск."""
        log.debug(
            "Start state {name}, stage {stage}".format(
                name=self.__name,
                stage=self.__stage,
            ),
        )
        new_state_data: NewStateData | None = None
        try:
            await self.__run_taskgroup()
        except* asyncio.TimeoutError:
            self.__except_timeout()
        except* NewStateException as exc:
            new_state_data = self.__except_new_state(exc)
        log.debug(
            "End state {name}, stage {stage}".format(
                name=self.__name,
                stage=self.__stage,
            ),
        )
        if new_state_data is not None:
            raise NewStateException.reraise(new_state_data, self.__name)

    def config_timeout(
        self,
        timeout: float,
        to_state: StatesEnum | None,
    ) -> None:
        """Изменить таймаут на выполнение."""
        self.__timeout = timeout
        self.__timeout_to_state = to_state

    async def __run_taskgroup(self) -> None:
        """Запуск."""
        async with asyncio.TaskGroup() as tg:
            self.__create_tasks(tg)

    def __create_tasks(self, tg: asyncio.TaskGroup) -> None:
        """Создание группы задач."""
        if self.__callbacks is None:
            return
        for task in self.__callbacks:
            tg.create_task(
                asyncio.wait_for(
                    fut=self.__coro_wrapper(task),
                    timeout=self.__timeout,
                ),
            )

    def __except_timeout(self) -> None:
        """Обработка превышения времени выполнения."""
        log.debug(EXC_TIMEOUT.format(name=self.__name, stage=self.__stage))
        if self.__timeout_to_state is None:
            msg = EXC_TIMEOUT_WITHOUT_TARGET.format(
                base_msg=EXC_TIMEOUT.format(
                    name=self.__name,
                    stage=self.__stage,
                ),
            )
            log.error(msg)
            raise StateMachineError(msg)
        raise NewStateException(
            new_state=self.__timeout_to_state,
        )

    def __except_new_state(
        self,
        exc: ExceptionGroup[NewStateException],
    ) -> NewStateData:
        """Обработка перехода в новое состояние."""
        new_state_data = exc.exceptions[0]
        if isinstance(new_state_data, NewStateException):
            exc_data = new_state_data.exception_data
            log.debug(
                "State {name}, stage {stage}, new state: {new_name}".format(
                    name=self.__name,
                    stage=self.__stage,
                    new_name=exc_data.new_state,
                ),
            )
            return exc_data
        raise StateMachineError
