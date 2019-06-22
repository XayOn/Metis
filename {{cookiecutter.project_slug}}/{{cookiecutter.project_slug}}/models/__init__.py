from contextlib import suppress
import configparser
import functools

import aiohttp
import aiozipkin as az


async def setup_models(app):
    """Setup models."""
    HTTPModel.app = app

    zipkin_address = None
    with suppress(configparser.NoSectionError):
        zipkin_address = app['config'].get('monitoring', 'zipkin_url')

    app['tracer'] = None
    if zipkin_address:
        # Only setup zipkin if it has been configured.
        # This way we avoid zipkin warnings
        app['tracer'] = await az.create(zipkin_address,
                                        az.create_endpoint("AIOHTTP_CLIENT"))
        az.setup(app, app['tracer'])

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
        if cls.app['tracer']:
            with cls.app['tracer'].new_trace() as span:
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
        if attr in aiohttp.hdrs.METH_ALL:
            return functools.partial(self.send_action, attr)
        return super().__getattribute__(attr)
