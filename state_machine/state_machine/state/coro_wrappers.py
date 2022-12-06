"""Обертки для запуска корутин."""


import asyncio

from ..typings import TCallback


class CoroWrappers(object):
    """Обертки для запуска корутин."""

    @staticmethod
    async def infinite(coro_func: TCallback) -> None:
        """Корутина вызывается в цикле бесконечно."""
        while True:  # noqa: WPS457
            await coro_func()
            await asyncio.sleep(0)

    @staticmethod
    async def single(coro_func: TCallback) -> None:
        """Корутина вызывается один раз."""
        await coro_func()
