import asyncio
import logging
from typing import Callable, Dict, Optional

from http_client import AsyncHttpClient, HttpClient, HttpClientExceptions
from rabbit_client import AsyncRabbitConsumerDurable
from schemas import MiscSettings, RabbitMQSettings, WorkerSettings


async def async_message_handler(http_client: HttpClient, test_url: str) -> bool:
    for _ in range(0, 5):
        try:
            r = await http_client.get(test_url)
        except HttpClientExceptions:
            await asyncio.sleep(5)
            continue
        if r.status_code == 200:
            logging.info('Successfully processed message.')
            break
        await asyncio.sleep(5)
    else:
        logging.error('Can not process message.')
        return False
    return True


async def setup_worker(
        worker_id: int,
        message_handler: Callable,
        message_handler_kwargs: Optional[Dict] = None,
) -> AsyncRabbitConsumerDurable:
    rabbit_settings = RabbitMQSettings()
    worker = AsyncRabbitConsumerDurable(worker_id)
    worker.set_consume_func(function=message_handler, func_kwargs=message_handler_kwargs)
    await worker.init_conn(**rabbit_settings.dict())
    return worker


if __name__ == '__main__':
    misc_settings = MiscSettings()
    worker_settings = WorkerSettings()
    logging.basicConfig(level=misc_settings.log_level.value)
    loop = asyncio.get_event_loop()
    for i in range(worker_settings.num_workers):
        task = loop.create_task(
            setup_worker(
                worker_id=i,
                message_handler_kwargs={
                    'test_url': worker_settings.url,
                    'http_client': AsyncHttpClient,
                },
                message_handler=async_message_handler,
            ),
            name=f'worker_{i}',
        )
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.warning('^C detected. Bye.')
