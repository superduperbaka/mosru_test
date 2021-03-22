import asyncio
import logging
import time
import uuid
from abc import ABCMeta, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Optional

import aiormq
import pika
import pika.exceptions
import aio_pika


class RabbitClientException(Exception):
    pass


class ConnectionNotInitializedException(RabbitClientException):
    pass


class ConnectionException(RabbitClientException):
    pass


class CredentialsException(RabbitClientException):
    pass


class RabbitClient(metaclass=ABCMeta):
    logger: logging.Logger

    @abstractmethod
    def close_conn(self):
        pass


class SyncRabbitProducerDurable(RabbitClient, metaclass=ABCMeta):
    conn: pika.adapters.blocking_connection.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel
    _task_queue: str

    def __init__(
            self,
            producer_id: str = str(uuid.uuid4()),
    ):
        self.logger = logging.getLogger(f'producer_{producer_id}')

    def init_conn(
            self,
            host: str,
            port: int,
            v_host: str,
            user: str,
            password: str,
            task_queue: str,
    ):

        for _ in range(5):
            try:
                self._connect(
                    host=host,
                    port=port,
                    v_host=v_host,
                    user=user,
                    password=password,
                    task_queue=task_queue,
                )
                break
            except pika.exceptions.AMQPConnectionError:
                self.logger.warning('Can\'t connect to rabbit. Try to reconnect.')
                time.sleep(5)
        else:
            logging.error('Can establish connection with rabbit service.')
            raise ConnectionException()
        self._task_queue = task_queue

    def _connect(
            self,
            host: str,
            port: int,
            v_host: str,
            user: str,
            password: str,
            task_queue: str,
    ):
        credentials = pika.PlainCredentials(
                username=user,
                password=password,
            )
        conn_parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=v_host,
            credentials=credentials,
        )
        self.conn = pika.BlockingConnection(parameters=conn_parameters)
        self.channel = self.conn.channel()
        self.channel.queue_declare(
            queue=task_queue,
            durable=True,
        )

    def produce(self, message: bytes):
        self.logger.debug(f'Sending message {str(message)}.')
        if not getattr(self, 'channel', None):
            raise ConnectionNotInitializedException()
        self.channel.basic_publish(
            exchange='',
            routing_key=self._task_queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        self.logger.debug('Sent message.')

    def close_conn(self):
        self.logger.debug('Closing connection.')
        if not self.channel.is_closed:
            self.channel.close()
        if not self.conn.is_closed:
            self.conn.close()


class AsyncRabbitConsumerDurable(RabbitClient, metaclass=ABCMeta):
    conn: aio_pika.connection.Connection
    queue: aio_pika.queue.Queue
    custom_consume_function: Callable[[Any], Awaitable[bool]]
    custom_consume_function_kwargs: Optional[Dict]

    def __init__(self, worker_id: int):
        self.logger = logging.getLogger(f'worker_{worker_id}')

    async def init_conn(
            self,
            host: str,
            port: int,
            v_host: str,
            user: str,
            password: str,
            task_queue: str,
    ):
        for _ in range(5):
            try:
                await self._connect(
                    host=host,
                    port=port,
                    v_host=v_host,
                    user=user,
                    password=password,
                    task_queue=task_queue,
                )
                break
            except ConnectionError:
                self.logger.warning('Can\'t connect to rabbit. Try to reconnect.')
                await asyncio.sleep(5)
            except aiormq.exceptions.ProbableAuthenticationError:
                raise CredentialsException()
        else:
            logging.error('Can establish connection with rabbit service.')
            raise ConnectionException()

    async def _connect(
            self,
            host: str,
            port: int,
            v_host: str,
            user: str,
            password: str,
            task_queue: str,
    ):
        self.conn = await aio_pika.connect(
            host=host,
            port=port,
            virtualhost=v_host,
            login=user,
            password=password,
        )

        channel = await self.conn.channel()
        await channel.set_qos(prefetch_count=1)

        self.queue = await channel.declare_queue(
            task_queue,
            durable=True,
        )
        await self.queue.consume(self._on_message)

    def set_consume_func(
            self,
            function: Callable[[Any], Awaitable[bool]],
            func_kwargs: Optional[Dict],
    ):
        self.custom_consume_function = function
        self.custom_consume_function_kwargs = func_kwargs

    async def _on_message(self, message: aio_pika.IncomingMessage):
        logging.debug(f'Received message {str(message.body)}.')
        if getattr(self, 'custom_consume_function', None):
            if not await self.custom_consume_function(**self.custom_consume_function_kwargs):
                self.logger.error('Failed process message.')
                message.nack()
                return
        self.logger.info('Message has been successfully processed.')
        message.ack()

    async def close_conn(self):
        if not self.conn.is_closed:
            self.logger.debug('Closing connection.')
            await self.conn.close()
