"""Исключения."""

from typing import NamedTuple, Self

from .states_enum import StatesEnum


class NewStateData(NamedTuple):
    """Данные, передаваемые при генерации исключения."""

    active_state: StatesEnum | None
    new_state: StatesEnum


class NewStateException(Exception):  # noqa: N818
    """Переход к новому состоянию."""

    def __init__(
        self,
        new_state: StatesEnum,
        new_state_data: NewStateData | None = None,
    ) -> None:
        """Переход к новому состоянию."""
        self.__exc_data: NewStateData

        if new_state_data is None:
            self.__exc_data = NewStateData(
                active_state=None,
                new_state=new_state,
            )
        else:
            self.__exc_data = new_state_data

    @classmethod
    def reraise(
        cls,
        new_state_data: NewStateData,
        active_state: StatesEnum,
    ) -> Self:
        """Перевызвать исключение."""
        return cls(
            new_state=new_state_data.new_state,
            new_state_data=NewStateData(
                active_state=active_state,
                new_state=new_state_data.new_state,
            ),
        )

    @property
    def exception_data(self) -> NewStateData:
        """Данные, сохраненные при вызове исключения."""
        return self.__exc_data


class StateMachineError(Exception):
    """Ошибка работы машины состояний."""

    def __init__(self, message: str = "") -> None:
        """Ошибка работы машины состояний."""
        self.__message: str

        self.__message = message

    @property
    def message(self) -> str:
        """Сообщение."""
        return self.__message


class StateTimeoutError(Exception):
    """Превышение времени выполнения."""
