"""Состояние."""

from typing import Final, Self

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..shared import exc_group_to_exc
from ..states_enum import StatesEnum
from .coro_wrappers import CoroWrappers
from .stage_callbacks import StageCallbacks, TCallbackCollection

EXC_NO_ON_RUN: Final[str] = "No callbacks on on_run input, state: {name}"
EXC_COMPL_NO_NEWSTATE: Final[
    str
] = "State '{name}' completed, but NewStateException not raised."

DEFAULT_TIMEOUT: Final[float] = 2.0


class State(object):
    """Состояние."""

    def __init__(  # noqa: WPS211
        self,
        name: StatesEnum,
        on_run: TCallbackCollection,
        on_enter: TCallbackCollection | None = None,
        on_exit: TCallbackCollection | None = None,
    ) -> None:
        """Состояние.

        Parameters
        ----------
        name: StatesEnum
            Название состояния из перечисления
        on_enter: TCallbackCollection
            Функции для выполения в стадии on_enter
        on_run: TCallbackCollection
            Функции для выполения в стадии on_run
        on_exit: TCallbackCollection
            Функции для выполения в стадии on_exit

        Raises
        ------
        StateMachineError
            не указаны задачи on_run
        """
        self.__name: StatesEnum
        self.__on_enter: StageCallbacks
        self.__on_run: StageCallbacks
        self.__on_exit: StageCallbacks
        self.__new_state_data: NewStateData | None

        if not on_run:
            raise StateMachineError(EXC_NO_ON_RUN.format(name=name))
        self.__name = name
        self.__on_enter = StageCallbacks(
            callbacks=on_enter,
            timeout=DEFAULT_TIMEOUT,
            timeout_to_state=None,
            name=self.__name,
            stage="on_enter",
            coro_wrapper=CoroWrappers.single,
        )
        self.__on_run = StageCallbacks(
            callbacks=on_run,
            timeout=None,
            timeout_to_state=None,
            name=self.__name,
            stage="on_run",
            coro_wrapper=CoroWrappers.infinite,
        )
        self.__on_exit = StageCallbacks(
            callbacks=on_exit,
            timeout=DEFAULT_TIMEOUT,
            timeout_to_state=None,
            name=self.__name,
            stage="on_exit",
            coro_wrapper=CoroWrappers.single,
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
        await self.__run_on_exit()
        if self.__new_state_data is None:
            raise StateMachineError(
                EXC_COMPL_NO_NEWSTATE.format(name=self.__name),
            )
        raise NewStateException.reraise(
            new_state_data=self.__new_state_data,
            active_state=self.__name,
        )

    def config_timeout_on_enter(
        self,
        timeout: float,
        to_state: StatesEnum | None = None,
    ) -> Self:
        """Установить таймаут для стадии on_enter.

        Parameters
        ----------
        timeout: float
            время таймаута. По-умолчанию 2.0 c
        to_state
            в какое состояние перейти после истечения времени.
            Если задано None, то возникнет исключение StateMachineError.
            По-умолчанию None.

        Returns
        -------
        Измененный объект состояния
        """
        self.__on_enter.config_timeout(timeout, to_state)
        return self

    def config_timeout_on_run(
        self,
        timeout: float,
        to_state: StatesEnum | None = None,
    ) -> Self:
        """Установить таймаут для стадии on_run.

        Parameters
        ----------
        timeout: float
            время таймаута. По-умолчанию ограничений нет.
        to_state
            в какое состояние перейти после истечения времени.
            Если задано None, то возникнет исключение StateMachineError.
            По-умолчанию None.

        Returns
        -------
        Измененный объект состояния
        """
        self.__on_run.config_timeout(timeout, to_state)
        return self

    def config_timeout_on_exit(
        self,
        timeout: float,
        to_state: StatesEnum | None = None,
    ) -> Self:
        """Установить таймаут для стадии on_exit.

        Parameters
        ----------
        timeout: float
            время таймаута. По-умолчанию 2.0 c
        to_state
            в какое состояние перейти после истечения времени.
            Если задано None, то возникнет исключение StateMachineError.
            По-умолчанию None.

        Returns
        -------
        Измененный объект состояния
        """
        self.__on_exit.config_timeout(timeout, to_state)
        return self

    async def __run_on_enter(self) -> None:
        state_machine_error: str | None = None
        try:
            await self.__on_enter.run()
        except* NewStateException as exc_gr:
            self.__new_state_data = exc_group_to_exc(exc_gr).exception_data
        except* StateMachineError as exc_gr:
            state_machine_error = exc_group_to_exc(exc_gr).message
        if state_machine_error is not None:
            raise StateMachineError(state_machine_error)

    async def __run_on_run(self) -> None:
        if self.__new_state_data is not None:
            return
        state_machine_error: str | None = None
        try:
            await self.__on_run.run()
        except* NewStateException as exc_gr:
            self.__new_state_data = exc_group_to_exc(exc_gr).exception_data
        except* StateMachineError as exc_gr:
            state_machine_error = exc_group_to_exc(exc_gr).message
        if state_machine_error is not None:
            raise StateMachineError(state_machine_error)

    async def __run_on_exit(self) -> None:
        state_machine_error: str | None = None
        try:
            await self.__on_exit.run()
        except* NewStateException as exc_gr:
            self.__new_state_data = exc_group_to_exc(exc_gr).exception_data
        except* StateMachineError as exc_gr:
            state_machine_error = exc_group_to_exc(exc_gr).message
        if state_machine_error is not None:
            raise StateMachineError(state_machine_error)
