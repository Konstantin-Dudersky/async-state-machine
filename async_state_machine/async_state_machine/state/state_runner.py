"""Рабочая логика State."""

from typing import Final, Self

from ..exceptions import NewStateData, NewStateException, StateMachineError
from ..shared import exc_group_to_exc
from ..states_enum import StatesEnum
from .stage_callbacks import StageCallbacks

EXC_COMPL_NO_NEWSTATE: Final[
    str
] = "State '{name}' completed, but NewStateException not raised."


class StateRunner(object):
    """Рабочая логика State."""

    def __init__(
        self,
        name: StatesEnum,
        on_enter: StageCallbacks,
        on_run: StageCallbacks,
        on_exit: StageCallbacks,
    ) -> None:
        """Рабочая логика State."""
        self.__name: StatesEnum
        self.__on_enter: StageCallbacks
        self.__on_run: StageCallbacks
        self.__on_exit: StageCallbacks
        self.__new_state_data: NewStateData | None

        self.__name = name
        self.__on_enter = on_enter
        self.__on_run = on_run
        self.__on_exit = on_exit
        self.__new_state_data = None

    @property
    def name(self) -> StatesEnum:
        """Имя состояния."""
        return self.__name

    async def run(self) -> None:
        """Задача для асинхронного выполнения, вызывается из StateMachine."""
        self.__new_state_data = None
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

    def config_logging(self, logging_level: int) -> Self:
        """Конфигурировать уровень логгирования."""
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
