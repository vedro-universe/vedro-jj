import asyncio
from asyncio import AbstractEventLoop, Task
from functools import partial
from threading import Thread
from typing import Any, List, Type, Union

from aiohttp import web
from jj import default_app, default_handler
from jj.middlewares import SelfMiddleware
from jj.mock import Mock
from jj.resolvers import Registry, ReversedResolver
from jj.runners import AppRunner
from jj.servers import Server
from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import CleanupEvent, StartupEvent

from ._interceptor import Interceptor, InterceptorType

__all__ = ("VedroJJ", "VedroJJPlugin", "interceptor",)


_interceptors: List[InterceptorType] = []


def interceptor(fn: InterceptorType) -> InterceptorType:
    _interceptors.append(fn)
    return fn


@Interceptor(_interceptors)
class _Mock(Mock):
    pass


class VedroJJPlugin(Plugin):
    def __init__(self, config: Type["VedroJJ"]) -> None:
        super().__init__(config)
        self._host = config.host
        self._port = config.port
        self._threaded = config.threaded
        self._server: Union[Server, None] = None
        self._task: Union["Task[Any]", None] = None
        self._thread: Union[Thread, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(StartupEvent, self.on_startup) \
                  .listen(CleanupEvent, self.on_cleanup)

    def _create_server(self, loop: AbstractEventLoop) -> Server:
        resolver = ReversedResolver(Registry(), default_app, default_handler)
        runner = partial(AppRunner, resolver=resolver, middlewares=[SelfMiddleware(resolver)])
        return Server(loop, runner, web.TCPSite)  # type: ignore

    def _serve_mock_threaded(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self._server = self._create_server(loop)
        self._server.start(_Mock(), self._host, self._port)
        try:
            self._server.serve()
        finally:
            self._server.shutdown()

        asyncio.set_event_loop(None)

    def on_startup(self, event: StartupEvent) -> None:
        if self._threaded:
            self._thread = Thread(target=self._serve_mock_threaded, daemon=True)
            self._thread.start()
        else:
            self._server = self._create_server(asyncio.get_event_loop())
            self._server.start(_Mock(), self._host, self._port)
            self._task = asyncio.create_task(self._server._serve())

    async def on_cleanup(self, event: CleanupEvent) -> None:
        if self._server:
            self._server.cleanup()

        if self._thread:
            self._thread.join(1.0)
            self._thread = None

        if self._task:
            await self._task
            self._task = None


class VedroJJ(PluginConfig):
    plugin = VedroJJPlugin

    host: str = "0.0.0.0"
    port: int = 8080

    # Start mock in a separate thread
    # Mandatory if blocking calls are used
    threaded: bool = True
