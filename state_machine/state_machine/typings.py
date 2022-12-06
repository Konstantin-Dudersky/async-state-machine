"""Типы данных для подксказок типов."""

from typing import Callable, Coroutine, Iterable

TCallback = Callable[[], Coroutine[None, None, None]]

TCallbackCollection = Iterable[TCallback]
