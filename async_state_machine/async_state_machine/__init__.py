"""Диаграмма состояний."""

from enum import auto as enum_auto

from loguru import logger

from .exceptions import NewStateException, StateMachineError
from .state import State
from .state_machine import StateMachine
from .states_enum import StatesEnum

__all__ = [
    "NewStateException",
    "State",
    "StateMachine",
    "StatesEnum",
    "StateMachineError",
    "enum_auto",
]

logger.disable(__name__)
