"""Диаграмма состояний."""

from enum import auto as enum_auto

from .exceptions import NewStateException
from .state import State
from .state_machine import StateMachine
from .states_enum import StatesEnum

__all__ = [
    "NewStateException",
    "State",
    "StateMachine",
    "StatesEnum",
    "enum_auto",
]
