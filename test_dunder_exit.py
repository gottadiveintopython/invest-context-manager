from contextlib import ExitStack, AsyncExitStack
from functools import partial
import pytest



class Method:
    def __init__(self):
        self.log = []

    def __enter__(self):
        self.log.append("__enter__")

    def __exit__(self, *__):
        self.log.append("__exit__")


class Slots:
    __slots__ = ("__exit__", "log", )

    def __init__(self):
        self.log = []
        self.__exit__ = partial(Method.__exit__, self)

    __enter__ = Method.__enter__


class Dict:
    def __init__(self):
        self.log = []
        self.__exit__ = partial(Method.__exit__, self)

    __enter__ = Method.__enter__


@pytest.mark.parametrize("cm_cls", [Method, Slots, Dict])
def test_with_statement(cm_cls):
    cm = cm_cls()
    with cm:
        pass
    assert cm.log == ["__enter__", "__exit__"]


@pytest.mark.parametrize("cm_cls", [Method, Slots, Dict])
def test_exit_stack(cm_cls):
    cm = cm_cls()
    with ExitStack() as stack:
        stack.enter_context(cm)
    assert cm.log == ["__enter__", "__exit__"]


@pytest.mark.parametrize("cm_cls", [Method, Slots, Dict])
def test_async_exit_stack(cm_cls):
    cm = cm_cls()

    async def run():
        async with AsyncExitStack() as stack:
            stack.enter_context(cm)
    with pytest.raises(StopIteration):
        run().send(None)
    assert cm.log == ["__enter__", "__exit__"]
