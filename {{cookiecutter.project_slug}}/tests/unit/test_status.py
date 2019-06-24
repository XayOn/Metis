async def test_status(aiohttp_client, aiohttp_app):
    """Test status endpoint.

    Use this as an example of how to make tests of an endpoint.
    """
    from {{cookiecutter.project_slug}} import get_app_version
    client = await aiohttp_client(aiohttp_app)
    url = f'/api/{get_app_version("v")}/'
    result = await client.get(url + 'status')
    await result.json() == {'status': 0}
