from asyncio import iscoroutinefunction
from typing import Awaitable, Callable, List, Optional, Union, cast

import jj
from jj.apps import AbstractApp as App
from jj.handlers import HandlerFunction as Handler
from jj.requests import Request
from jj.resolvers import Resolver
from jj.responses import StreamResponse as Response

__all__ = ("Interceptor", "InterceptorType",)


SyncInterceptor = Callable[[Request, Response], Response]
AsyncInterceptor = Callable[[Request, Response], Awaitable[Response]]
InterceptorType = Union[SyncInterceptor, AsyncInterceptor]


class Interceptor(jj.Middleware):
    def __init__(self, interceptors: List[InterceptorType],
                 resolver: Optional[Resolver] = None) -> None:
        super().__init__(resolver)
        self._interceptors = interceptors

    async def do(self, request: Request, handler: Handler, app: App) -> Response:
        response = await handler(request)
        if "x-jj-remote-mock" in request.headers:
            return response

        for interceptor in self._interceptors:
            if iscoroutinefunction(interceptor):
                res = await cast(AsyncInterceptor, interceptor)(request, response)
            else:
                res = cast(SyncInterceptor, interceptor)(request, response)

            if isinstance(res, Response):
                response = res
            elif res is not None:
                raise ValueError("Interceptor must return response (or None)")

        return response
