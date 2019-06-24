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

    def __init__(self, request):
        """Setup request for this instance."""
        self.request = request

    def set_headers(self):
        """Set default headers.

        Dont forget to call this method with super() on subclasses,
        otherwise aiozipkin tracing would be lost
        """
        if self.request.headers.get(az.helpers.SAMPLED_ID_HEADER):
            # Relay aiozipkin headers if they exist.
            hdrs = (az.helpers.TRACE_ID_HEADER, az.helpers.SPAN_ID_HEADER,
                    az.helpers.PARENT_ID_HEADER, az.helpers.FLAGS_HEADER,
                    az.helpers.SAMPLED_ID_HEADER)
            return {a: b for a, b in self.request.headers.items() if a in hdrs}
        if self.app[APP_AIOZIPKIN_KEY]:
            with self.app[APP_AIOZIPKIN_KEY].new_trace(sampled=True) as span:
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

    def get_url(self, endpoint):
        """Extract URL for a specific endpoint."""
        return self.config['url'].format(endpoint=endpoint)

    async def send_action(self, method, endpoint, data):
        """Send action against the service."""
        return await self.app['http_session'].request(
            method.upper(),
            self.get_url(endpoint),
            json=data,
            headers=self.set_headers())

    def __getattribute__(self, attr):
        if attr.upper() in aiohttp.hdrs.METH_ALL:
            return functools.partial(self.send_action, attr.upper())
        return super().__getattribute__(attr)
