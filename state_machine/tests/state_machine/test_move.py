import asyncio
import pytest

import state_machine as sm


class States(sm.StatesEnum):
    """Перечень состояний."""

    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_move_between_states() -> None:
    """Происходит ли переход между состояниями."""

    async def on_run_state_1() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_run_state_2() -> None:
        while True:
            await asyncio.sleep(2)

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
        },
        enum=States,
        init_state=States.state_1,
    )

    async def run():
        task = state_machine.task()
        try:
            await asyncio.wait_for(task, 0.1)
        except asyncio.TimeoutError:
            pass

    asyncio.run(run())

    assert state_machine.active_state.name == States.state_2


def test_exc_name_not_found() -> None:
    """Переход в состояние с неизвестным названием."""

    async def on_run_state_1() -> None:
        raise sm.NewStateException("UNKNOWN_STATE")  # pyright: ignore

    state_machine = sm.StateMachine(
        states={
            sm.State(
                name=States.state_1,
                on_run=[on_run_state_1],
            ),
            sm.State(
                name=States.state_2,
                on_run=[],
            ),
        },
        enum=States,
        init_state=States.state_1,
    )
    with pytest.raises(sm.StateMachineError) as exc:
        asyncio.run(state_machine.task())
    assert str(exc.value) == "State with name UNKNOWN_STATE not found."
