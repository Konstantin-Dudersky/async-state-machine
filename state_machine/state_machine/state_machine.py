"""Диаграмма состояний."""

import asyncio
from typing import Final, Iterable, Type

from .exceptions import NewStateException, StateMachineError
from .state import State
from .states_enum import StatesEnum

EXC_REUSE_STATE: Final[str] = "Several use state with name: {name}"
EXC_NOT_USED_STATES: Final[str] = "Need to define states: {states}"
EXC_NAME_NOT_FOUND: Final[str] = "State with name {name} not found."


class StateMachine(object):
    """Диаграмма состояний."""

    def __init__(
        self,
        states: Iterable[State],
        init_state: StatesEnum,
        enum: Type[StatesEnum],
    ) -> None:
        """Определение диаграммы состояний."""
        self.__active_state: State
        self.__enum_values: set[str]
        self.__states: Iterable[State]

        self.__states = states
        self.__enum_values = {state.value for state in enum}
        self.__check_names()
        self.__active_state = self.__set_init_state(init_state)

    @property
    def active_state(self) -> State:
        """Активное состояние."""
        return self.__active_state

    async def task(self) -> None:
        """Задача для асинхронного выполнения."""
        try:
            await self.__active_state.task()
        except NewStateException as exc:
            self.__active_state = self.__find_state_by_name(
                exc.exception_data.new_state,
            )
        await asyncio.sleep(0.1)

    def __set_init_state(self, init_state: StatesEnum) -> State:
        for state in self.__states:
            if state.name == init_state:
                return state
        raise ValueError(
            "Init state {0} not found in states array".format(init_state),
        )

    def __check_names(self) -> None:
        names = self.__extract_names()
        if len(names) != len(self.__enum_values):
            not_used_states = self.__enum_values.difference(names)
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

    def __find_state_by_name(self, name: StatesEnum) -> State:
        for state in self.__states:
            if state.name == name:
                return state
        raise StateMachineError(EXC_NAME_NOT_FOUND.format(name=name))
