import asyncio
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_timeout_exc() -> None:
    async def func() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_enter=[func],
        timeout_on_enter=0.1,
        on_run=[func],
    )
    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert (
            exc.message
            == "Timeout occur in state state_1, stage on_enter, but target state not specified"
        )


def test_timeout_to_state() -> None:
    async def func() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_enter=[func],
        timeout_on_enter=0.1,
        timeout_on_enter_to_state=States.state_2,
        on_run=[func],
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        print(exc)
        assert exc.exception_data.new_state == States.state_2


def test_from_enter_to_exit() -> None:
    """Если срабатывает исключение во время on_enter, то переходим в on_exit.

    on_run не должен выполняться.
    """

    class StateException(Exception):
        pass

    async def on_enter() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_run() -> None:
        raise StateException("on_run must be omitted")

    async def on_exit() -> None:
        raise StateException("on_exit")

    state = sm.State(
        name=States.state_1,
        on_enter=[on_enter],
        on_run=[on_run],
        on_exit=[on_exit],
    )

    try:
        asyncio.run(state.run())
    except* StateException as exc_gr:
        assert str(exc_gr.exceptions[0]) == "on_exit"
