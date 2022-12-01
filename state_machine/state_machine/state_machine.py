"""Базовый класс для диаграммы состояний."""

import asyncio
from typing import Iterable

from .state import State
from .states_enum import StatesEnum


class StateMachine(object):
    """Базовый класс для диаграммы состояний."""

    def __init__(
        self,
        states: Iterable[State],
        init_state: StatesEnum,
    ) -> None:
        # TODO проверка, что в не используется одинаковый StatesEnum
        # TODO проверка, что используются все возможные StatesEnum
        self.__active_state: State
        self.__states: Iterable[State]

        self.__states = states
        self.__active_state = self.__set_init_state(init_state)

    @property
    def active_state(self) -> State:
        """Активное состояние."""
        return self.__active_state

    async def task(self) -> None:
        await self.__active_state.task()
        await asyncio.sleep(2)

    def __set_init_state(self, init_state: StatesEnum) -> State:
        for state in self.__states:
            if state.enum_value == init_state:
                return state
        raise ValueError(
            "Init state {0} not found in states array".format(init_state),
        )
