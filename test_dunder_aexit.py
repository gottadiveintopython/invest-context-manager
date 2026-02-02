from contextlib import AsyncExitStack
from functools import partial
import pytest


class Method:
    def __init__(self):
        self.log = []

    async def __aenter__(self):
        self.log.append("__aenter__")

    async def __aexit__(self, *__):
        self.log.append("__aexit__")


class Slots:
    __slots__ = ("__aexit__", "log", )

    def __init__(self):
        self.log = []
        self.__aexit__ = partial(Method.__aexit__, self)

    __aenter__ = Method.__aenter__


class Dict:
    def __init__(self):
        self.log = []
        self.__aexit__ = partial(Method.__aexit__, self)

    __aenter__ = Method.__aenter__


@pytest.mark.parametrize("cm_cls", [Method, Slots, Dict])
def test_with_statement(cm_cls):
    cm = cm_cls()

    async def run():
        async with cm:
            pass
    with pytest.raises(StopIteration):
        run().send(None)
    assert cm.log == ["__aenter__", "__aexit__"]


@pytest.mark.parametrize("cm_cls", [Method, Slots, Dict])
def test_exit_stack(cm_cls):
    cm = cm_cls()

    async def run():
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(cm)
    with pytest.raises(StopIteration):
        run().send(None)
    assert cm.log == ["__aenter__", "__aexit__"]
