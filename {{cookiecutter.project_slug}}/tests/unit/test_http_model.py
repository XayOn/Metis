import pytest
import json
from aioresponses import aioresponses

from hypothesis import given
import hypothesis.strategies as st


@pytest.mark.asyncio
@pytest.mark.parametrize('method', ['get', 'post', 'put'])
@given(st.text(), st.dictionaries(st.text(), st.text()))
async def test_httpmodel(testmodel, method, expected, endpoint):
    """Base http model always acts as a proxy against an external API.

    This tests any method with any content is returned as-is
    """
    from {{cookiecutter.project_slug}}.models import HTTPModel

    class TestModel(HTTPModel):
        """FakeModel."""

    model = testmodel(TestModel, None)
    model.mock(method, endpoint, expected)
    result = await getattr(model, method)(endpoint, expected)
    assert await result.json() == expected


@pytest.mark.parametrize("name", ['foo', 'bar', 'baz'])
def test_service_name(name):
    from {{cookiecutter.project_slug}}.models import HTTPModel
    class_ = type(name, (HTTPModel, ), {})
    assert class_(None).service_name == f'{name.lower()}_service'


async def test_zipkin_headers():
    pass
