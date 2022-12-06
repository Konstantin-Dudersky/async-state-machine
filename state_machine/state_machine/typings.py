"""Типы данных для подксказок типов."""

from typing import Callable, Coroutine, Iterable

TCallCoro = Callable[[], Coroutine[None, None, None]]

TCoroCollection = Iterable[TCallCoro]
