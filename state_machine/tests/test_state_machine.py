import pytest

import state_machine as sm


class States(sm.StatesEnum):
    """Перечень состояний."""

    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_not_all_states() -> None:
    """Определены не все состояния."""
    with pytest.raises(sm.StateMachineError):
        sm.StateMachine(
            states={
                sm.State(
                    name=States.state_1,
                    on_run=[],
                ),
            },
            states_enum=States,
            init_state=States.state_1,
        )


def test_reuse_names() -> None:
    """Дублирование названий."""
    with pytest.raises(sm.StateMachineError):
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
            states_enum=States,
            init_state=States.state_1,
        )
