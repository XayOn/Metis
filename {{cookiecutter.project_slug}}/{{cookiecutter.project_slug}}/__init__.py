"""Base API app.

Setup automatically:

    - logging
    - tracing
    - routes
    - API versioning with pyproject version
"""
from pathlib import Path
from contextlib import suppress
import asyncio
import configparser
import sys
import os
import uuid
import warnings

import yaml
import semver
import toml

from aiohttp import web
from aiohttp_apiset import SwaggerRouter
from aiohttp_apiset.middlewares import jsonify
import aiohttp

import aiozipkin as az
from aiozipkin.aiohttp_helpers import APP_AIOZIPKIN_KEY
from aiozipkin.aiohttp_helpers import REQUEST_AIOZIPKIN_KEY
from aiozipkin.aiohttp_helpers import middleware_maker

from cleo import Command
from cleo import Application

import pygogo

from .routes import setup_routes
from .models import setup_models

warnings.filterwarnings('ignore', category=yaml.YAMLLoadWarning)


def get_app_version(prefix):
    """Get app version for automatic versioning."""
    pyproject = toml.load(Path(__file__).parent.parent / 'pyproject.toml')
    version = semver.parse(pyproject['tool']['poetry']['version'])['major']
    return f'{prefix}{version}'


@web.middleware
async def log_middleware(request, handler):
    """Logging middleware, setups a uuid4 for each request.

    This allows us to trace requests between different services.
    """
    request['logger'] = request.app['logger'].get_logger(uid=uuid.uuid4())
    return await handler(request)


async def init_tracer(app, tracer_key=APP_AIOZIPKIN_KEY):
    """Async init tracer."""
    zipkin_address = None
    with suppress(configparser.NoSectionError):
        zipkin_address = app['config'].get('monitoring', 'zipkin_url')

    app[tracer_key] = None
    if zipkin_address:
        # Only setup zipkin if it has been configured.
        # This way we avoid zipkin warnings
        name = __name__.split('.')[0]
        app[tracer_key] = await az.create(zipkin_address,
                                          az.create_endpoint(name))


def setup_tracer(app,
                 tracer_key=APP_AIOZIPKIN_KEY,
                 skip_routes=None,
                 request_key=REQUEST_AIOZIPKIN_KEY):
    mdwr = middleware_maker(skip_routes=skip_routes,
                            tracer_key=tracer_key,
                            request_key=request_key)
    app.middlewares.append(mdwr)

    # register cleanup signal to close zipkin transport connections
    async def close_aiozipkin(app: Application) -> None:
        await app[tracer_key].close()

    app.on_cleanup.append(close_aiozipkin)

    return app


def get_subapp(prefix, config_file, debug):
    """Return a main app object.

    - Setup configuration
    - Setup logger
    - Setup routes (with automatic API version prefix in the URL)
    """

    app = web.Application(router=SwaggerRouter(version_ui=3),
                          middlewares=[jsonify])
    setup_routes(app)
    setup_tracer(app)
    app.on_startup.append(setup_models)
    app.on_startup.append(init_tracer)
    app.router._swagger_ui = prefix + 'apidoc/'

    app['config'] = configparser.ConfigParser()
    app['config'].read(config_file)
    app['logger'] = pygogo.Gogo(
        __name__,
        low_formatter=pygogo.formatters.structured_formatter,
        verbose=debug)
    app['logger'].get_logger().info(f'Swagger available on {prefix}apidoc/')

    return app


def get_app(config='etc/config.ini', debug=False):
    """Get app."""
    prefix = f'/api/{get_app_version("v")}/'
    sub_app = get_subapp(prefix, config, debug)

    app = web.Application()
    app.add_subapp(prefix, sub_app)
    return app


class ServerCommand(Command):
    """Base project.

    start_server
        {--host=0.0.0.0 : Host to listen on}
        {--port=8080 : Port to listen on}
        {--config=config.ini : Config file}
        {--debug : Debug and verbose mode}
    """

    def handle(self):
        """Handle command."""
        app = get_app(self.option('config'), self.option('debug'))
        host = os.getenv('HOST', self.option('host'))
        port = int(os.getenv('PORT', self.option('port')))
        web.run_app(app, host, port)


class StatusCommand(Command):
    """Check service status.

    check_status
        {--host=0.0.0.0 : Host where the service is listening}
        {--port=8080 : Port where the service is listening}
    """

    def handle(self):
        """Handle command."""
        app = get_app('', False)
        sub_app = app._subapps[0]
        return asyncio.get_event_loop().run_until_complete(
            self.get_status(sub_app))

    async def get_status(self, app):
        segment = app.router['global_status'].url_for()
        host = os.getenv('HOST', self.option('host'))
        port = int(os.getenv('PORT', self.option('port')))
        async with aiohttp.ClientSession() as session:
            result = await session.get(f"http://{host}{port}{segment}")
            response = await result.json()
            self.line(await result.text())
        sys.exit(response['status'])


def main():
    """Main."""
    application = Application()
    application.add(ServerCommand())
    application.add(StatusCommand())
    application.run()
