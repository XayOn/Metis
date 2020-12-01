from metis.cli import ServeCommand
from metis.app import MetisApplication
from metis.model import HTTPModel
from cleo import Application
from aiohttp import web


class HTTPBin(HTTPModel):
    """Httpbin base client."""
    def status(self):
        """Inter-service status check

        If a status method is defined, it will be called each time the /status
        endpoint of this service is called.
        """
        return self.post('post', {1: 2})['json']['1'] == 2


async def handler(request):
    """Handler

    ---

    summary: Call httpbin post endpoint
    tags:
      - test
    responses:
      '200':
        description: Example handler
    """
    request['logger'].debug("Example debug log")
    return web.json_response({'ok': await HTTPBin().post('post', {1: 2})})


class MyCustomStartServerCommand(ServeCommand):
    def get_app(self):
        """Get main app.

        Configure routes and so on here.
        """
        app = MetisApplication('metis')
        app.add_routes([web.post('post', handler)])
        return app


def main():
    """Main."""
    app = Application()
    app.add(MyCustomStartServerCommand())
    app.run()


if __name__ == "__main__":
    main()
