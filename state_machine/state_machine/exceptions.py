"""Исключения."""

from typing import NamedTuple, Self

from .states_enum import StatesEnum


class NewStateExceptionData(NamedTuple):
    """Данные, передаваемые при генерации исключения."""

    active_state: StatesEnum | None
    new_state: StatesEnum


class NewStateException(Exception):  # noqa: N818
    """Переход к новому состоянию."""

    def __init__(
        self,
        new_state: StatesEnum,
        active_state: StatesEnum | None = None,
    ) -> None:
        """Переход к новому состоянию."""
        self.__exc_data: NewStateExceptionData

        self.__exc_data = NewStateExceptionData(
            active_state=active_state,
            new_state=new_state,
        )

    @classmethod
    def reraise(
        cls,
        exc_data: NewStateExceptionData,
        active_state: StatesEnum,
    ) -> Self:
        """Перевызвать исключение."""
        return cls(
            new_state=exc_data.new_state,
            active_state=active_state,
        )

    @property
    def exception_data(self) -> NewStateExceptionData:
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
