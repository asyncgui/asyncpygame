import pytest


def test_close_a_fully_consumed_async_generator_1():
    async def create_agen():
        yield

    async def async_fn(agen):
        await agen.asend(None)
        with pytest.raises(StopAsyncIteration):
            await agen.asend(None)
        await agen.aclose()
        await agen.aclose()

    with pytest.raises(StopIteration):
        async_fn(create_agen()).send(None)


def test_close_a_fully_consumed_async_generator_2():
    async def create_agen():
        return
        yield

    async def async_fn(agen):
        with pytest.raises(StopAsyncIteration):
            await agen.asend(None)
        await agen.aclose()
        await agen.aclose()

    with pytest.raises(StopIteration):
        async_fn(create_agen()).send(None)


def test_close_a_unstarted_async_generator():
    async def create_agen():
        yield

    async def async_fn(agen):
        await agen.aclose()
        await agen.aclose()

    with pytest.raises(StopIteration):
        async_fn(create_agen()).send(None)


def test_close_a_partially_consumed_async_generator():
    async def create_agen():
        yield

    async def async_fn(agen):
        await agen.asend(None)
        await agen.aclose()
        await agen.aclose()

    with pytest.raises(StopIteration):
        async_fn(create_agen()).send(None)
