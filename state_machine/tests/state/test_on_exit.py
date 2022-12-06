import asyncio

import pytest
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()
    state_3 = sm.enum_auto()


def test_timeout_exc() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(10)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        on_exit=[on_exit],
    ).config_timeout_on_exit(1.0)

    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert (
            exc.message
            == "Timeout occur in state state_1, stage on_exit, but target state not specified"
        )


def test_timeout_to_state() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        on_exit=[on_exit],
    ).config_timeout_on_exit(0.1, States.state_2)

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
    )
    with pytest.raises(sm.NewStateException) as exc:
        asyncio.run(state.run())
    assert exc.value.exception_data.new_state == States.state_3
