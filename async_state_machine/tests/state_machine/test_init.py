import asyncio
import pytest

import async_state_machine as sm


from async_state_machine.state_machine import (
    EXC_NOT_USED_STATES,
    EXC_REUSE_STATE,
)


class States(sm.StatesEnum):
    """Перечень состояний."""

    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_exc_not_all_states() -> None:
    """Определены не все состояния."""

    async def on_run():
        await asyncio.sleep(10)

    with pytest.raises(sm.StateMachineError) as exc:
        sm.StateMachine(
            states={
                sm.State(
                    name=States.state_1,
                    on_run=[on_run],
                ),
            },
            states_enum=States,
            init_state=States.state_1,
        )
    assert exc.value.message == EXC_NOT_USED_STATES.format(
        states={States.state_2.value},
    )


def test_exc_reuse_names() -> None:
    """Дублирование названий."""

    async def on_run():
        pass

    with pytest.raises(sm.StateMachineError) as exc:
        sm.StateMachine(
            states={
                sm.State(
                    name=States.state_1,
                    on_run=[on_run],
                ),
                sm.State(
                    name=States.state_1,
                    on_run=[on_run],
                ),
                sm.State(
                    name=States.state_2,
                    on_run=[on_run],
                ),
            },
            states_enum=States,
            init_state=States.state_1,
        )
    assert exc.value.message == EXC_REUSE_STATE.format(
        name=States.state_1,
    )


def test_init_state() -> None:
    """Начальное состояние устанавливается правильно."""

    async def on_run():
        pass

    state_machine = sm.StateMachine(
        states={
            sm.State(
                name=States.state_1,
                on_run=[on_run],
            ),
            sm.State(
                name=States.state_2,
                on_run=[on_run],
            ),
        },
        states_enum=States,
        init_state=States.state_2,
    )
    assert state_machine.active_state == States.state_2
