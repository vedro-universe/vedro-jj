import jj
import pytest
from aiohttp import ClientSession
from jj.mock import Mocked, mocked
from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as ScenarioScheduler
from vedro.core import Report
from vedro.events import CleanupEvent, StartupEvent

import vedro_jj
from vedro_jj import VedroJJPlugin


def make_startup_event():
    return StartupEvent(ScenarioScheduler([]))


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
async def plugin(dispatcher: Dispatcher) -> VedroJJPlugin:
    class RemoteMock(vedro_jj.VedroJJ):
        threaded = False

    plugin = VedroJJPlugin(RemoteMock)
    plugin.subscribe(dispatcher)

    await dispatcher.fire(make_startup_event())
    yield plugin
    await dispatcher.fire(CleanupEvent(Report()))


@pytest.fixture()
async def plugin_threaded(dispatcher: Dispatcher) -> VedroJJPlugin:
    class RemoteMockThreaded(vedro_jj.VedroJJ):
        threaded = True

    plugin = VedroJJPlugin(RemoteMockThreaded)
    plugin.subscribe(dispatcher)

    await dispatcher.fire(make_startup_event())
    yield plugin
    await dispatcher.fire(CleanupEvent(Report()))


@pytest.fixture()
async def mock() -> Mocked:
    async with mocked(jj.match("*"), jj.Response()) as mock:
        yield mock


async def test_mock(plugin: VedroJJPlugin, mock: Mocked):
    async with ClientSession() as session:
        response = await session.get("http://localhost:8080")
    assert response.status == 200


async def test_mock_threaded(plugin_threaded: VedroJJPlugin, mock: Mocked):
    async with ClientSession() as session:
        response = await session.get("http://localhost:8080")
    assert response.status == 200
