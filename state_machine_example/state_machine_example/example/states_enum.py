import state_machine as sm


class StatesEnum(sm.StatesEnum):
    run = sm.enum_auto()
    pause = sm.enum_auto()
