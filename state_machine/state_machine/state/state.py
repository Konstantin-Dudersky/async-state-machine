"""Строитель для создания State."""

import logging
from dataclasses import dataclass
from typing import Final, Self

from ..exceptions import StateMachineError
from ..states_enum import StatesEnum
from .coro_wrappers import CoroWrappers
from .stage_callbacks import StageCallbacks, TCallbackCollection
from .state_runner import StateRunner

EXC_NO_ON_RUN: Final[str] = "No callbacks on on_run input, state: {name}"
DEFAULT_TIMEOUT: Final[float] = 2.0


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


@dataclass
class _StageData(object):
    callbacks: TCallbackCollection | None
    timeout: float | None
    timeout_to_state: StatesEnum | None


class State(object):
    """Строитель для создания State."""

    def __init__(  # noqa: WPS211
        self,
        name: StatesEnum,
        on_run: TCallbackCollection,
        on_enter: TCallbackCollection | None = None,
        on_exit: TCallbackCollection | None = None,
    ) -> None:
        """Строитель для создания State.

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
        self.__on_enter: _StageData
        self.__on_run: _StageData
        self.__on_exit: _StageData
        self.__logging_level: int

        if not on_run:
            raise StateMachineError(EXC_NO_ON_RUN.format(name=name))
        self.__name = name
        self.__on_enter = _StageData(
            callbacks=on_enter,
            timeout=DEFAULT_TIMEOUT,
            timeout_to_state=None,
        )
        self.__on_run = _StageData(
            callbacks=on_run,
            timeout=None,
            timeout_to_state=None,
        )
        self.__on_exit = _StageData(
            callbacks=on_exit,
            timeout=DEFAULT_TIMEOUT,
            timeout_to_state=None,
        )
        self.__logging_level = logging.INFO

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
        self.__on_enter.timeout = timeout
        self.__on_enter.timeout_to_state = to_state
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
        self.__on_run.timeout = timeout
        self.__on_run.timeout_to_state = to_state
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
        self.__on_exit.timeout = timeout
        self.__on_exit.timeout_to_state = to_state
        return self

    def config_logging(self, logging_level: int) -> Self:
        """Конфигурировать уровень логгирования."""
        log.setLevel(logging_level)
        return self

    def build(self) -> StateRunner:
        """Создание состояния.

        Вызывается из StateMachine.
        """
        return StateRunner(
            name=self.__name,
            on_enter=StageCallbacks(
                callbacks=self.__on_enter.callbacks,
                timeout=self.__on_enter.timeout,
                timeout_to_state=self.__on_enter.timeout_to_state,
                name=self.__name,
                stage="on_enter",
                coro_wrapper=CoroWrappers.single,
                logging_level=self.__logging_level,
            ),
            on_run=StageCallbacks(
                callbacks=self.__on_run.callbacks,
                timeout=self.__on_run.timeout,
                timeout_to_state=self.__on_run.timeout_to_state,
                name=self.__name,
                stage="on_run",
                coro_wrapper=CoroWrappers.infinite,
                logging_level=self.__logging_level,
            ),
            on_exit=StageCallbacks(
                callbacks=self.__on_exit.callbacks,
                timeout=self.__on_exit.timeout,
                timeout_to_state=self.__on_exit.timeout_to_state,
                name=self.__name,
                stage="on_exit",
                coro_wrapper=CoroWrappers.single,
                logging_level=self.__logging_level,
            ),
        )
