import state_machine as sm


class StatesEnum(sm.StatesEnum):
    run = sm.enum_auto()
    pause = sm.enum_auto()


state_machine = sm.StateMachine(
    states=(
        sm.State(
            enum_value=StatesEnum.run,
            on_run=[],
        ),
        sm.State(
            enum_value=StatesEnum.pause,
            on_run=[],
        ),
    ),
    init_state=StatesEnum.pause,
)
