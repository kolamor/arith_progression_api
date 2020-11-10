from src.source import ArithmeticProgressionTask, QueueFactory, next_number_task
# import asyncio
import pytest


def test_tasks_number_gen():
    n = 1
    while n < 10:
        assert next_number_task() == n
        n += 1


templates_query = [{
        "count": 6,
        "delta": 2,
        "start": 1,
        "interval": 0.01
    }, # 7
    {
        "count": 7,
        "delta": 3,
        "start": 3,
        "interval": 1
    }  # 21
]


@pytest.mark.parametrize('query', templates_query)
@pytest.mark.asyncio
async def test_arith_task(query):
    async def coro(value):
        if not hasattr(coro, 'n'):
            coro.n = query['start']
        assert coro.n == value
        coro.n += query['delta']

    task = ArithmeticProgressionTask(number_task=1, **query)
    await task.run(iter_output=coro)