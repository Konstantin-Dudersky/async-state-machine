import pytest

import state_machine as sm


class States(sm.StatesEnum):
    """Перечень состояний."""

    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_exc_not_all_states() -> None:
    """Определены не все состояния."""
    with pytest.raises(sm.StateMachineError) as exc:
        sm.StateMachine(
            states={
                sm.State(
                    name=States.state_1,
                    on_run=[],
                ),
            },
            enum=States,
            init_state=States.state_1,
        )
    assert str(exc.value) == "Need to define states: {'state_2'}"


def test_exc_reuse_names() -> None:
    """Дублирование названий."""
    with pytest.raises(sm.StateMachineError) as exc:
        sm.StateMachine(
            states={
                sm.State(
                    name=States.state_1,
                    on_run=[],
                ),
                sm.State(
                    name=States.state_1,
                    on_run=[],
                ),
                sm.State(
                    name=States.state_2,
                    on_run=[],
                ),
            },
            enum=States,
            init_state=States.state_1,
        )
    assert str(exc.value) == "Several use state with name: state_1"


def test_init_state() -> None:
    """Начальное состояние устанавливается правильно."""
    state_machine = sm.StateMachine(
        states={
            sm.State(
                name=States.state_1,
                on_run=[],
            ),
            sm.State(
                name=States.state_2,
                on_run=[],
            ),
        },
        enum=States,
        init_state=States.state_2,
    )
    assert state_machine.active_state.name == States.state_2
