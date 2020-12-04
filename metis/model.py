import configparser
import functools

import aiozipkin as az
from aiozipkin.aiohttp_helpers import APP_AIOZIPKIN_KEY
from aiohttp_request import grequest
from environs import Env

import aiohttp
from odmantic import Model as _ODModel
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from .metis_logging import LoggableTaskMethodsClass


class HTTPModel(LoggableTaskMethodsClass):
    """Base HTTP Model.

    If you're accessing an external service, ITS MANDATORY to instance this
    class. If you use it directly, it'll cause a few issues (inconsistent
    config names, no aiohttp session available...
    """
    @property
    def app(self):
        return grequest.app

    @property
    def config(self):
        return grequest.app['application'].env

    def set_headers(self):
        """Set default headers.

        Dont forget to call this method with super() on subclasses,
        otherwise aiozipkin tracing would be lost
        """
        resend_headers = {
            a: grequest.headers.get(a)
            for a in self.config.list('RESEND_HEADERS')
        }
        headers = {}
        if grequest.headers.get(az.helpers.SAMPLED_ID_HEADER):
            # Relay aiozipkin headers if they exist.
            hdrs = (az.helpers.TRACE_ID_HEADER, az.helpers.SPAN_ID_HEADER,
                    az.helpers.PARENT_ID_HEADER, az.helpers.FLAGS_HEADER,
                    az.helpers.SAMPLED_ID_HEADER)
            headers = {a: b for a, b in grequest.headers.items() if a in hdrs}
        elif grequest.app.get(APP_AIOZIPKIN_KEY):  # pragma: nocover
            # TODO: Add mocked tests for trace generation
            with grequest.app[APP_AIOZIPKIN_KEY].new_trace(
                    sampled=True) as span:
                span.kind(az.CLIENT)
                headers = span.context.make_headers()
        return {**headers, **resend_headers}

    @property
    def service_name(self):
        """Automatically set this as a specific service."""
        return f'{self.__class__.__name__.upper()}'

    def get_url(self, endpoint):
        """Extract URL for a specific endpoint.
        Override this method if you need a more fine-grained approach
        """
        return self.svc_config('url').format(endpoint=endpoint)

    def svc_config(self, cfg_name):
        """Return a config for this specific service. will be uppercased."""
        return self.config(f'{self.service_name}_{cfg_name.upper()}')

    async def send_action(self, method, endpoint, data):
        """Send action against the service."""
        url = self.get_url(endpoint)
        grequest['logger'].debug('Starting request {} to {}', method, url)
        response = await grequest.app['http_session'].request(
            method.upper(), url, json=data, headers=self.set_headers())
        if response.headers['Content-Type'] == 'application/json':
            return await response.json()
        return await response.text()

    @classmethod
    async def setup(cls, app):
        """Setup models.

        On an http model this implies creating an aiohttp clientsession that
        will be used later on (see `send_action`)
        """
        if cls.__subclasses__():
            cfg = app['application'].env
            app['http_session'] = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    sock_read=cfg.float('SOCK_READ', 40),
                    sock_connect=cfg.float('SOCK_CONNECT', 3)),
                connector=aiohttp.TCPConnector(
                    verify_ssl=cfg.bool('SSL', False),
                    limit=cfg.int('LIMIT', 30),
                ))

    async def teardown(cls):
        """Cleanup http session."""
        if cls.subclasses():
            await app['http_session'].close()

    def __getattribute__(self, attr):
        """Allow usage of subclasses as:

        class Foo(HTTPModel):
            pass

        await Foo().post('/bar')

        with all aiohttp-supported methods.
        """
        if attr.upper() in aiohttp.hdrs.METH_ALL:
            return functools.partial(self.send_action, attr.upper())
        return super().__getattribute__(attr)


class MongoModel(_ODModel, LoggableTaskMethodsClass):
    """Mongomodel"""
    @classmethod
    async def setup(cls, app):
        """Setup models.

        On an http model this implies creating an aiohttp clientsession that
        will be used later on (see `send_action`)
        """
        cfg = app['application'].env
        if cfg('MONGODB', None):
            client = AsyncIOMotorClient(cfg('MONGODB'))
            app['mongodb'] = AIOEngine(motor_client=client)

    @classmethod
    async def count(cls, *queries):
        return await grequest.app['mongodb'].count(cls, *queries)

    async def delete(self):
        return await grequest.app['mongodb'].delete(self)

    @classmethod
    async def find_one(cls, *args, **kwargs):
        return await grequest.app['mongodb'].find_one(cls, *args, **kwargs)

    @classmethod
    async def save(self):
        await grequest.app['mongodb'].save(self)
