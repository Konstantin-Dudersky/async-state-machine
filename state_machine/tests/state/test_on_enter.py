import asyncio
import state_machine as sm


class States(sm.StatesEnum):
    state_1 = sm.enum_auto()
    state_2 = sm.enum_auto()


def test_on_enter_timeout_exc() -> None:
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


def test_on_enter_timeout_to_state() -> None:
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
