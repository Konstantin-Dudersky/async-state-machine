import asyncio
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_empty_list() -> None:
    try:
        sm.State(
            name=States.state_1,
            on_run=[],
        )
    except sm.StateMachineError as exc:
        assert exc.message == "No callbacks on on_run input, state: state_1"


def test_timeout_exc() -> None:
    async def on_run() -> None:
        await asyncio.sleep(1000)

    state = (
        sm.State(
            name=States.state_1,
            on_run=[on_run],
        )
        .config_timeout_on_run(0.1)
        .build()
    )

    try:
        asyncio.run(state.run())
    except sm.StateMachineError as exc:
        assert (
            exc.message
            == "Timeout occur in state state_1, stage on_run, but target state not specified"
        )


def test_timeout_to_state() -> None:
    async def on_run() -> None:
        await asyncio.sleep(1000)

    state = (
        sm.State(
            name=States.state_1,
            on_run=[on_run],
        )
        .config_timeout_on_run(0.1, States.state_2)
        .build()
    )

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2


def test_new_state() -> None:
    """Переход в новое состояние."""

    async def on_run() -> None:
        raise sm.NewStateException(States.state_2)

    state = sm.State(
        name=States.state_1,
        on_run=[on_run],
    ).build()

    try:
        asyncio.run(state.run())
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2


def test_callback_infinite() -> None:
    """Функции on_run вызываются в цикле бесконечно."""

    class TestClass:
        def __init__(self) -> None:
            self.value: int = 0

        async def on_run(self) -> None:
            self.value += 1
            if self.value > 10:
                raise sm.NewStateException(States.state_2)

    test_class = TestClass()

    state = sm.State(
        name=States.state_1,
        on_run=[test_class.on_run],
    ).build()

    try:
        asyncio.run(asyncio.wait_for(state.run(), 0.2))
    except sm.NewStateException as exc:
        assert exc.exception_data.new_state == States.state_2
    except asyncio.TimeoutError:
        assert False
