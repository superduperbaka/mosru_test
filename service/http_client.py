from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Union, Awaitable

import httpx


class HttpClientExceptions(Exception):
    pass


class HttpClientConnectionException(HttpClientExceptions):
    pass


class HttpClientInvalidURLException(HttpClientExceptions):
    pass


class HttpClientCookieException(HttpClientExceptions):
    pass


class HttpClientStreamException(HttpClientExceptions):
    pass


@dataclass
class HttpResultProxy:
    status_code: int


class HttpClient(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get(url: str) -> Union[HttpResultProxy, Awaitable[HttpResultProxy]]:
        pass


class AsyncHttpClient(HttpClient, metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    async def get(url: str) -> HttpResultProxy:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url)
                return HttpResultProxy(status_code=r.status_code)
        except httpx.HTTPError:
            raise HttpClientConnectionException(f'Connection error occurred'
                                                f' for "{url}".')
        except httpx.InvalidURL:
            raise HttpClientInvalidURLException(f'URL "{url}" is improperly formed'
                                                f' or cannot be parsed.')
        except httpx.CookieConflict:
            raise HttpClientCookieException('Attempted to lookup a cookie by name,'
                                            ' but multiple cookies existed.')
        except httpx.StreamError:
            raise HttpClientStreamException('Accessing the request stream'
                                            ' in an invalid way.')
