import platform
from metis.cli import ServeCommand
from metis.app import MetisApplication
from metis.model import HTTPModel, MongoModel
from cleo import Application
from laozi import Laozi
from aiohttp import web


class HTTPBin(HTTPModel):
    def status(self):
        return self.post('post', {1: 2})['json']['1'] == 2


class HTTPBinResponses(MongoModel):
    name: str
    response: dict


MAPPING = {'starting_HTTPBin().post': {'message': 'starting_httpbin_request'}}


def custom_formatter(record):
    """In case you want to map the not-so-nice automatic debug messages

    This also illustrates a different logging custom format printing all extra
    variables.
    """
    record['extra'].update(MAPPING.get(record['message'], record['message']))
    record['extra']['splunk'] = Laozi.parse(record)
    return "{extra[splunk]}\n"


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
    resp = await HTTPBin().post('post', {1: 2})
    await HTTPBinResponses(name='ok', response=resp).save()
    return web.json_response({'ok': resp})


class CustomLogApplication(MetisApplication):
    def setup_logger(self, logger):
        logger.add('{platform.node()}.info',
                   format=custom_formatter,
                   level='DEBUG')


class MyCustomStartServerCommand(ServeCommand):
    def get_app(self):
        """Get main app.

        Configure routes and so on here.
        """
        app = CustomLogApplication('metis')
        app.add_routes([web.post('post', handler)])
        return app


def main():
    """Main."""
    app = Application()
    app.add(MyCustomStartServerCommand())
    app.run()


if __name__ == "__main__":
    main()
