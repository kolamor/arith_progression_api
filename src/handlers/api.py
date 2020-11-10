from aiohttp.web import View, json_response
import logging
import weakref
from ..source import ArithmeticProgressionTask, QueueFactory, Queue

logger = logging.getLogger(__name__)


class Root(View):
    async def get(self):
        app_name = self.request.app['config'].get('app_name', 'default_app')
        context = {
            'test': app_name
        }
        return json_response(context, status=200)


class ArithmeticProgressionView(View):

    async def post(self):
        # TODO validation json
        json_request = await self.request.json()
        queue_factory: QueueFactory = self.request.app['queue_factory']
        number_task = self.request.app['next_number_task']()
        task = ArithmeticProgressionTask(number_task=number_task, **json_request)
        weakset: weakref.WeakSet = self.request.app['weakref_tasks']
        weakset.add(task)
        queue: Queue = queue_factory.get_queue()
        await queue.put(task)
        context = {
            "status": "task put in queue",
            "task number": number_task
        }
        return json_response(context, status=200)


class Statistic(View):

    async def get(self):
        weakset: weakref.WeakSet = self.request.app['weakref_tasks']
        context = []
        for task in weakset:
            context.append(task.status_fields)

        context.sort(key=lambda x: x['number_task'])
        return json_response(context, status=200)

