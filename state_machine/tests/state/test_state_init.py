import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_no_on_run() -> None:
    try:
        sm.State(
            name=States.state_1,
            on_run=[],
        )
    except sm.StateMachineError as exc:
        assert exc.message == "No callbacks on on_run input, state: state_1"
