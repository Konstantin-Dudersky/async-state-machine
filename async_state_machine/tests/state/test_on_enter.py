import asyncio
import async_state_machine as sm

from async_state_machine.state.stage_callbacks import (
    EXC_TIMEOUT_WITHOUT_TARGET,
    EXC_TIMEOUT,
)


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_timeout_exc() -> None:
    async def func() -> None:
        await asyncio.sleep(1000)

    state = (
        sm.State(
            name=States.state_1,
            on_enter=[func],
            on_run=[func],
        )
        .config_timeout_on_enter(0.1)
        .build()
    )
    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert exc.message == EXC_TIMEOUT_WITHOUT_TARGET.format(
            base_msg=EXC_TIMEOUT.format(
                name=States.state_1,
                stage="on_enter",
            )
        )


def test_timeout_to_state() -> None:
    async def func() -> None:
        await asyncio.sleep(1000)

    state = (
        sm.State(
            name=States.state_1,
            on_enter=[func],
            on_run=[func],
        )
        .config_timeout_on_enter(0.1, States.state_2)
        .build()
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        print(exc)
        assert exc.exception_data.new_state == States.state_2


def test_from_enter_to_exit() -> None:
    """Если срабатывает исключение во время on_enter, то переходим в on_exit.

    on_run не должен выполняться.
    """

    class StateException(Exception):
        pass

    async def on_enter() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_run() -> None:
        raise StateException("on_run must be omitted")

    async def on_exit() -> None:
        raise StateException("on_exit")

    state = sm.State(
        name=States.state_1,
        on_enter=[on_enter],
        on_run=[on_run],
        on_exit=[on_exit],
    ).build()

    try:
        asyncio.run(state.run())
    except* StateException as exc_gr:
        assert str(exc_gr.exceptions[0]) == "on_exit"
