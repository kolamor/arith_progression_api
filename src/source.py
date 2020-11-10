import asyncio
import weakref
from typing import Any, Union, Awaitable, Optional
import datetime
import logging

logger = logging.getLogger(__file__)


def next_number_task(start_task: int = 1):
    """Генератор номеров задач"""
    def gen():
        value = start_task
        while True:
            yield value
            value += 1
    if not hasattr(next_number_task, '_gen'):
        next_number_task._gen = gen()
    return next(next_number_task._gen)


class Queue:
    _queue: asyncio.Queue
    tasks: weakref.WeakSet

    def __init__(self, max_size: int = 0):
        self._queue = asyncio.Queue(max_size)
        self.tasks = weakref.WeakSet()

    def qsize(self) -> int:
        return self._queue.qsize()

    async def put(self, item: 'ArithmeticProgressionTask'):
        self.tasks.add(item)
        r = await self._queue.put(item=item)
        item.set_status_in_queue()
        return r

    async def get(self) -> Any:
        q_item = await self._queue.get()
        self._queue.task_done()
        return q_item


class QueueFactory:

    _queues: Union[weakref.WeakSet]
    __multi_queue_mode: bool
    __single_queue: Optional[Queue]
    _queue_maxsize = 0

    def __init__(self, multi_queue_mode: bool = False):
        self.__multi_queue_mode = multi_queue_mode
        self._queues = weakref.WeakSet()
        if not multi_queue_mode:
            self.__single_queue = Queue(max_size=self._queue_maxsize)
            self._queues.add(self.__single_queue)

    def get_queue(self) -> Queue:
        if self.__multi_queue_mode:
            queue = Queue(max_size=self._queue_maxsize)
            self._queues.add(queue)
            return queue
        else:
            return self.__single_queue


class ArithmeticProgressionTask:
    _status: str
    count: int
    delta: float
    start: float
    result: float
    interval: float
    start_date: datetime.datetime
    number_task: int

    def __init__(self, count: int, delta: float, interval: float, start: float, number_task: Optional[int] = None):
        if interval <= 1:
            raise ValueError(f"interval {interval} must be > 1")
        self.count = count
        self.delta = delta
        self.start = start
        self.interval = interval
        self.number_task = number_task

    async def run(self, iter_output: Union[Awaitable, None] = None) -> float:
        if not iter_output:
            iter_output = self.iter_output
        self.start_date = datetime.datetime.now()
        self.set_status_in_process()
        gen = self.gen_results()
        async for res in gen:
            self.result = res
            await iter_output(self.result)
        self._status = 'done'
        return self.result

    async def iter_output(self, value):
        print(f'task {self.number_task} default iter output', value)

    async def gen_results(self):
        result = self.start
        yield result
        for n in range(self.count - 1):
            result += self.delta
            await asyncio.sleep(self.interval)
            yield result

    @property
    def status(self):
        return self._status

    @property
    def status_fields(self):
        items = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        try:
            items['start_date'] = str(self.start_date)
        except AttributeError:
            items['start_date'] = None
        items['status'] = self._status
        return items

    def set_status_in_process(self) -> None:
        self._status = 'process'

    def set_status_in_queue(self) -> None:
        self._status = 'queue'


async def workers_creator(app):
    print("start subscribe")
    semaphore = asyncio.Semaphore(app['config'].get('max_workers', 100))
    queue_factory: QueueFactory = app['queue_factory']
    queue: Queue = queue_factory.get_queue()
    while True:
        await semaphore.acquire()
        task: ArithmeticProgressionTask = await queue.get()
        asyncio.ensure_future(worker(task=task, semaphore=semaphore))
        await asyncio.sleep(0)


async def worker(task: ArithmeticProgressionTask, semaphore: asyncio.Semaphore):
    try:
        # Добавляем корутину в аргументы iter_output если нужна обработка результата на каждую итерацию
        await task.run()
    except Exception as e:
        logger.error(f"worker {e} :: {e.args}")
    finally:
        semaphore.release()


async def main():
    item = {
        'count': 20,
        'delta': 2,
        'start': 1,
        'interval': 3
    }
    t = ArithmeticProgressionTask(number_task=next_number_task(), **item)
    res = await t.run()
    print('vvv', res)
    print(t.status_fields)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())



