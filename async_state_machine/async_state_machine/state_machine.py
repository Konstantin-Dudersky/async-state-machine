"""Диаграмма состояний."""

import asyncio
from typing import Final, Iterable, Self, Type

from .exceptions import NewStateException, StateMachineError
from .state import State, StateRunner
from .states_enum import StatesEnum

EXC_NAME_NOT_FOUND: Final[str] = "State with name {name} not found."
EXC_NOT_USED_STATES: Final[str] = "Need to define states: {states}"
EXC_REUSE_STATE: Final[str] = "Several use state with name: {name}"


class StateMachine(object):
    """Диаграмма состояний."""

    def __init__(
        self,
        states: Iterable[State],
        states_enum: Type[StatesEnum],
        init_state: StatesEnum,
    ) -> None:
        """Определение диаграммы состояний."""
        self.__active_state: StateRunner
        self.__state_names: set[str]
        self.__states: Iterable[StateRunner]

        self.__states = [state.build() for state in states]
        self.__state_names = {state.value for state in states_enum}
        self.__check_state_names()
        self.__active_state = self.__set_init_state(init_state)

    @property
    def active_state(self) -> StatesEnum:
        """Активное состояние."""
        return self.__active_state.name

    async def run(self) -> None:
        """Задача для асинхронного выполнения."""
        while True:
            try:
                await self.__active_state.run()
            except NewStateException as exc:
                new_state = exc.exception_data.new_state
                self.__active_state = self.__find_state_by_name(new_state)
            await asyncio.sleep(0)

    def config_logging(self, logging_level: int) -> Self:
        """Конфигурировать уровень логгирования."""
        # log.setLevel(logging_level)
        for state in self.__states:
            state.config_logging(logging_level)
        return self

    def __set_init_state(self, init_state: StatesEnum) -> StateRunner:
        for state in self.__states:
            if state.name == init_state:
                return state
        raise ValueError(
            "Init state {0} not found in states array".format(init_state),
        )

    def __check_state_names(self) -> None:
        names = self.__extract_names()
        if len(names) != len(self.__state_names):
            not_used_states = self.__state_names.difference(names)
            raise StateMachineError(
                EXC_NOT_USED_STATES.format(states=not_used_states),
            )

    def __extract_names(self) -> set[str]:
        names: set[str] = set()
        for state in self.__states:
            name = state.name.value
            if name in names:
                raise StateMachineError(EXC_REUSE_STATE.format(name=name))
            names.add(name)
        return names

    def __find_state_by_name(self, name: StatesEnum) -> StateRunner:
        for state in self.__states:
            if state.name == name:
                return state
        raise StateMachineError(EXC_NAME_NOT_FOUND.format(name=name))
