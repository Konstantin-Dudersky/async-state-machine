import asyncio
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_on_enter_timeout() -> None:
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


def test_on_enter_to_state() -> None:
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
        assert exc.exception_data.new_state == States.state_2


def test_on_run_timeout() -> None:
    async def on_run() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        timeout_on_run=0.1,
    )

    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert (
            exc.message
            == "Timeout occur in state state_1, stage on_run, but target state not specified"
        )


def test_on_run_to_state() -> None:
    async def on_run() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        timeout_on_run=0.1,
        timeout_on_run_to_state=States.state_2,
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2


def test_on_exit_timeout() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(10)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        timeout_on_run=2,
        timeout_on_run_to_state=States.state_2,
        on_exit=[on_exit],
        timeout_on_exit=1,
    )

    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert (
            exc.message
            == "Timeout occur in state state_1, stage on_exit, but target state not specified"
        )
    assert False


def test_on_exit_to_state() -> None:
    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    async def on_exit() -> None:
        await asyncio.sleep(1000)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
        on_exit=[on_exit],
        timeout_on_exit=0.1,
        timeout_on_exit_to_state=States.state_2,
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2
