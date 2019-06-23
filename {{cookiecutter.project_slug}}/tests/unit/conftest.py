from pathlib import Path

from aioresponses import aioresponses

import pytest


@pytest.fixture
def aiohttp_app():
    from {{cookiecutter.project_slug}} import get_app
    config_fixture = (Path(__file__).parent / 'fixtures' /
                      'config.ini').absolute()
    return get_app(config=config_fixture)


@pytest.fixture
def mock_aioresponse():
    with aioresponses(passthrough=['http://127.0.0.1:']) as m:
        yield m


@pytest.fixture
async def testmodel(aiohttp_client, aiohttp_app, mock_aioresponse):
    client = await aiohttp_client(aiohttp_app)

    def mock(obj, method, endpoint, data):
        return getattr(mock_aioresponse, method)(obj.get_url(endpoint),
                                                 payload=data)

    def generator(model, request):
        return type(
            model.__name__, (model, ), {
                'app': client._server.app._subapps[0],
                'set_headers': lambda _: {},
                'mock': mock
            })(request)

    return generator
