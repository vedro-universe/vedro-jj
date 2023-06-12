from typing import List
from unittest.mock import AsyncMock, Mock, sentinel

import pytest
from jj.apps import AbstractApp as App
from jj.handlers import HandlerFunction as Handler
from jj.requests import Request
from jj.resolvers import Resolver
from jj.responses import StreamResponse as Response
from pytest import raises

from vedro_jj import Interceptor, InterceptorType


@pytest.fixture()
def app():
    return Mock(App)


@pytest.fixture()
def handler():
    return AsyncMock(return_value=sentinel.response)


@pytest.fixture()
def req():
    return Mock(Request, headers={})


def interceptor_factory(interceptors: List[InterceptorType]) -> Interceptor:
    return Interceptor(interceptors, Mock(Resolver))


async def test_middleware(req: Request, handler: Handler, app: App):
    middleware = interceptor_factory([])

    response = await middleware.do(req, handler, app)

    assert response == sentinel.response


async def test_middleware_sync(req: Request, handler: Handler, app: App):
    mock = Mock(Response)

    def interceptor(req, res):
        return mock

    middleware = interceptor_factory([interceptor])

    response = await middleware.do(req, handler, app)
    assert response == mock


async def test_middleware_async(req: Request, handler: Handler, app: App):
    mock = Mock(Response)

    async def interceptor(req, res):
        return mock

    middleware = interceptor_factory([interceptor])

    response = await middleware.do(req, handler, app)
    assert response == mock


async def test_middleware_no_response(req: Request, handler: Handler, app: App):
    middleware = interceptor_factory([lambda req, res: None])

    response = await middleware.do(req, handler, app)

    assert response == sentinel.response


async def test_middleware_incorrect_response(req: Request, handler: Handler, app: App):
    middleware = interceptor_factory([lambda req, res: req])

    with raises(Exception) as exc:
        await middleware.do(req, handler, app)

    assert exc.type is ValueError
