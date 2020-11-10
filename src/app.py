import aiohttp
import asyncio
import logging
import weakref
from .source import Queue, next_number_task, QueueFactory, workers_creator
from src.routes import setup_routes


logger = logging.getLogger(__name__)


async def create_app(config: dict) -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    app['config'] = config
    setup_routes(app)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    config = app['config']
    app['next_number_task'] = next_number_task
    app['weakref_tasks'] = weakref.WeakSet()
    app['queue_factory'] = QueueFactory()
    asyncio.ensure_future(workers_creator(app=app)).add_done_callback(workers_creator_callback)


async def on_shutdown(app):
    # TODO создать мягкую остановку с таймаутом без приема requests
    print('on_shutdown')
    logger.info('on_shutdown')


def workers_creator_callback(*args, **kwargs):
    logger.debug(f" creator {args}, {kwargs}")