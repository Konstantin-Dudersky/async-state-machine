import asyncio

import pytest
import async_state_machine as sm

from async_state_machine.state.stage_callbacks import (
    EXC_TIMEOUT_WITHOUT_TARGET,
    EXC_TIMEOUT,
)


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()
    state_3 = sm.enum_auto()


def test_timeout_exc() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(10)

    state = (
        sm.State(
            name=States.state_1,
            on_run=[on_run],
            on_exit=[on_exit],
        )
        .config_timeout_on_exit(1.0)
        .build()
    )

    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert exc.message == EXC_TIMEOUT_WITHOUT_TARGET.format(
            base_msg=EXC_TIMEOUT.format(
                name=States.state_1,
                stage="on_exit",
            )
        )


def test_timeout_to_state() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(1000)

    state = (
        sm.State(
            name=States.state_1,
            on_run=[on_run],
            on_exit=[on_exit],
        )
        .config_timeout_on_exit(0.1, States.state_2)
        .build()
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2


def test_new_state() -> None:
    """Если во время on_exit сработало исключение NewStateException.

    Переходим на новое исключение, вне зависимости от on_enter, on_run.
    """

    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        raise sm.NewStateException(States.state_3)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        on_exit=[on_exit],
    ).build()

    with pytest.raises(sm.NewStateException) as exc:
        asyncio.run(state.run())
    assert exc.value.exception_data.new_state == States.state_3
