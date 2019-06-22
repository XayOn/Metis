import configparser
import functools

import aiozipkin as az
from aiozipkin.aiohttp_helpers import APP_AIOZIPKIN_KEY

import aiohttp


async def setup_models(app):
    """Setup models."""
    HTTPModel.app = app

    app['http_session'] = aiohttp.ClientSession()


class HTTPModel:
    """Base HTTP Model."""

    app = None

    @classmethod
    def set_headers(cls):
        """Set default headers.

        Dont forget to call this method with super() on subclasses, otherwise
        aiozipkin tracing would be lost
        """
        if cls.app[APP_AIOZIPKIN_KEY]:
            with cls.app[APP_AIOZIPKIN_KEY].new_trace() as span:
                span.kind(az.CLIENT)
                return span.context.make_headers()
        return {}

    @property
    def service_name(self):
        """Automatically set this as a specific service."""
        return f'{self.__class__.__name__.lower()}_service'

    @property
    def config(self):
        """Return config for this http service.

        Configuration entries are mandatory and should be

            [{class_name}_service]
            url = "http://.../{endpoint}/foo"
            secret = "foo"
            token = "bar"
        """
        return self.app['config'][self.service_name]

    async def send_action(self, method, endpoint, data):
        """Send action against the service."""
        return await self.app['http_session'].request(
            method.upper(),
            self.config['url'].format(endpoint=endpoint),
            json=data,
            headers=self.set_headers())

    def __getattribute__(self, attr):
        if attr.upper() in aiohttp.hdrs.METH_ALL:
            return functools.partial(self.send_action, attr.upper())
        return super().__getattribute__(attr)
