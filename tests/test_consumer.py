import logging
import time

import pytest

from service.consumer import async_message_handler
from service.rabbit_client import ConnectionException, CredentialsException


@pytest.mark.withrabbit
@pytest.mark.asyncio
async def test_consumer_network_exc(consumer):
    with pytest.raises(ConnectionException):
        await consumer.init_conn(
                host='localhost',
                port=65535,
                v_host='vhost',
                password='guest',
                user='guest',
                task_queue='',
            )


@pytest.mark.withrabbit
@pytest.mark.asyncio
async def test_consumer_credentials_exc(consumer):
    with pytest.raises(CredentialsException):
        await consumer.init_conn(
                host='localhost',
                port=5672,
                v_host='vhost',
                password='guest',
                user='guest',
                task_queue='',
            )


@pytest.mark.asyncio
@pytest.mark.slow
async def test_async_message_handler_failed(caplog, fake_http_client_fail):
    start_time = time.time()
    with caplog.at_level(logging.DEBUG):
        result = await async_message_handler(http_client=fake_http_client_fail, test_url='http://example.com')
        # return False
        assert not result
    # Logging message
    assert 'Can not process message' in caplog.text
    # grace period ~ 20 sec
    assert (time.time() - start_time) > 20.0


@pytest.mark.asyncio
async def test_async_message_handler_success(caplog, fake_http_client_success):
    with caplog.at_level(logging.DEBUG):
        result = await async_message_handler(http_client=fake_http_client_success, test_url='http://example.com')
        # return False
        assert result
    # Logging message
    assert 'Successfully processed message.' in caplog.text
