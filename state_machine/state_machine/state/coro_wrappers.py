import asyncio

from ..typings import TCallCoro


class CoroWrappers(object):
    @staticmethod
    async def infinite(coro_func: TCallCoro) -> None:
        """Корутина вызывается в цикле бесконечно."""
        while True:  # noqa: WPS457
            await coro_func()
            await asyncio.sleep(0)

    @staticmethod
    async def single(coro_func: TCallCoro) -> None:
        """Корутина вызывается один раз."""
        await coro_func()
