from typing import TypeVar


TException = TypeVar("TException", bound=Exception)


def exc_group_to_exc(exc_gr: ExceptionGroup[TException]) -> TException:
    return exc_gr.exceptions[0]  # pyright: ignore[reportGeneralTypeIssues]
