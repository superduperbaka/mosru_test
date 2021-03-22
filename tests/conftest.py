import os
import sys
from abc import ABC

import pytest
from starlette.testclient import TestClient # noqa

from service.backend import app
from service.http_client import AsyncHttpClient, HttpResultProxy
from service.rabbit_client import AsyncRabbitConsumerDurable, SyncRabbitProducerDurable

sys.path.append('%s/service' % os.path.realpath(os.path.curdir))


class FakeHttpClientFail(AsyncHttpClient, ABC):
    @staticmethod
    async def get(url: str, success: bool = True) -> HttpResultProxy:
        return HttpResultProxy(status_code=404)


class FakeHttpClientSuccess(AsyncHttpClient, ABC):
    @staticmethod
    async def get(url: str, success: bool = True) -> HttpResultProxy:
        return HttpResultProxy(status_code=200)


@pytest.fixture()
def backend_api() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture()
def producer() -> SyncRabbitProducerDurable:
    return SyncRabbitProducerDurable()


@pytest.fixture()
def consumer() -> AsyncRabbitConsumerDurable:
    return AsyncRabbitConsumerDurable(worker_id=1)


@pytest.fixture()
def fake_http_client_fail() -> FakeHttpClientFail:
    return FakeHttpClientFail()


@pytest.fixture()
def fake_http_client_success() -> FakeHttpClientSuccess:
    return FakeHttpClientSuccess()
