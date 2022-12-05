import asyncio

import pytest
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


class TestClass:
    def __init__(self) -> None:
        self.on_enter_executed = False
        self.on_run_executed = False
        self.on_exit_executed = False

    async def on_enter(self) -> None:
        self.on_enter_executed = True

    async def on_run(self) -> None:
        self.on_run_executed = True
        raise sm.NewStateException(States.state_2)

    async def on_exit(self) -> None:
        self.on_exit_executed = True


def test_all_callbacks_executed() -> None:
    """Все коллбеки выполняются."""
    test_class = TestClass()
    state_machine = sm.State(
        name=States.state_1,
        on_enter=[test_class.on_enter],
        on_run=[test_class.on_run],
        on_exit=[test_class.on_exit],
    )
    try:
        asyncio.run(state_machine.run())
    except sm.NewStateException:
        pass
    if not test_class.on_enter_executed:
        assert False
    if not test_class.on_run_executed:
        assert False
    if not test_class.on_exit_executed:
        assert False


def test_on_run_no_newstateexception() -> None:
    """on_run выполнился, но не было исключения."""

    async def wrong_on_run():
        pass

    state_machine = sm.State(
        name=States.state_1,
        on_run=[],
    )
    asyncio.run(state_machine.run())
    # with pytest.raises(sm.StateMachineError) as exc:
    #     asyncio.run(state_machine.run())
    # assert str(exc.value) == "State with name UNKNOWN_STATE not found."
