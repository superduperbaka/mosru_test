import pytest

from service.rabbit_client import ConnectionException, ConnectionNotInitializedException


def test_producer_not_init_exc(producer):
    with pytest.raises(ConnectionNotInitializedException):
        producer.produce(b'test')


@pytest.mark.withrabbit
@pytest.mark.slow
def test_producer_network_exc(producer):
    with pytest.raises(ConnectionException):
        producer.init_conn(
            host='localhost',
            port=65535,
            v_host='vhost',
            password='guest',
            user='guest',
            task_queue='',
        )


@pytest.mark.withrabbit
@pytest.mark.slow
def test_producer_wrong_credentials(producer):
    with pytest.raises(ConnectionException):
        producer.init_conn(
            host='localhost',
            port=5672,
            v_host='vhost',
            password='guest',
            user='guest',
            task_queue='',
        )
