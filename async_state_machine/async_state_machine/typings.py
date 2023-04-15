"""Типы данных для подксказок типов."""

from collections.abc import Awaitable, Callable, Iterable

TCallback = Callable[[], Awaitable[None]]
TCallbackCollection = Iterable[TCallback]
