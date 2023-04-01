import asyncio
import pytest

import async_state_machine as sm

from async_state_machine.state_machine import EXC_NAME_NOT_FOUND


class States(sm.StatesEnum):
    """Перечень состояний."""

    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()
    state_3 = sm.enum_auto()


def test_move_between_states() -> None:
    """Происходит ли переход между состояниями."""

    async def on_run_state_1() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_run_state_2() -> None:
        raise sm.NewStateException(States.state_3)

    async def on_run_state_3() -> None:
        await asyncio.sleep(10)

    import logging

    state_machine = sm.StateMachine(
        states={
            sm.State(
                name=States.state_1,
                on_run=[on_run_state_1],
            ),
            sm.State(
                name=States.state_2,
                on_run=[on_run_state_2],
            ),
            sm.State(
                name=States.state_3,
                on_run=[on_run_state_3],
            ),
        },
        states_enum=States,
        init_state=States.state_1,
    ).config_logging(logging.DEBUG)

    async def run():
        try:
            await asyncio.wait_for(state_machine.run(), 0.2)
        except asyncio.TimeoutError:
            pass

    asyncio.run(run())

    assert state_machine.active_state.name == States.state_3


def test_exc_name_not_found() -> None:
    """Переход в состояние с неизвестным названием."""

    async def on_run_state_1() -> None:
        raise sm.NewStateException("UNKNOWN_STATE")  # pyright: ignore

    async def on_run_state_2() -> None:
        pass

    state_machine = sm.StateMachine(
        states={
            sm.State(
                name=States.state_1,
                on_run=[on_run_state_1],
            ),
            sm.State(
                name=States.state_2,
                on_run=[on_run_state_2],
            ),
            sm.State(
                name=States.state_3,
                on_run=[on_run_state_2],
            ),
        },
        states_enum=States,
        init_state=States.state_1,
    )
    with pytest.raises(sm.StateMachineError) as exc:
        asyncio.run(state_machine.run())
    assert str(exc.value) == EXC_NAME_NOT_FOUND.format(name="UNKNOWN_STATE")
