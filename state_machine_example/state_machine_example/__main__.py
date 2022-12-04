import asyncio

import state_machine as sm


class StatesEnum(sm.StatesEnum):
    run = sm.enum_auto()
    pause = sm.enum_auto()


async def run_execute() -> None:
    print("run_execute 1")
    await asyncio.sleep(2)


async def run_execute2() -> None:
    print("run_execute 2")
    await asyncio.sleep(5)
    raise sm.NewStateException(StatesEnum.run)


async def run_on_exit() -> None:
    print("run exit")


state_machine = sm.StateMachine(
    states=(
        sm.State(
            name=StatesEnum.run,
            on_run=[run_execute, run_execute2],
            on_exit=[run_on_exit],
        ),
        sm.State(
            name=StatesEnum.pause,
            on_run=[],
        ),
    ),
    init_state=StatesEnum.run,
    enum=StatesEnum,
)


async def _main():
    await state_machine.task()


def main():
    asyncio.run(_main())
