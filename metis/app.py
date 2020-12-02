from importlib import resources, metadata
from contextlib import suppress
from functools import cached_property

from aiohttp_swagger3 import RapiDocUiSettings, SwaggerDocs
from aiohttp_swagger3.routes import _SWAGGER_SPECIFICATION, CustomEncoder

from aiozipkin.aiohttp_helpers import APP_AIOZIPKIN_KEY

import aiohttp

from .metis_logging import MetisLogger
from .model import HTTPModel, MongoModel

from environs import Env
import semver


class MetisApplication:
    """Main application, complements aiohttp application by adding:

        - Automatic endpoint versioning
        - Swagger3 pre-configured with package data
        - Environment configurations
        - Automatic models (with env configurations and magic-logging of
          coroutines

        It's mandatory to have an openapi.yml spec and an env file on your
        project's root dir.
        """
    def __init__(self, package_name: str = 'metis'):
        """Setup package name."""
        self.package_name = package_name
        with resources.path(self.package_name, '') as pack:
            self.package_directory = pack
        self.env = Env()
        self.env.read_env(".env", recurse=False)
        self.logger = MetisLogger.setup(self)

    def setup_logger(self, logger):
        """Setup logging here. logger is a `loguru` instance"""
        return

    @cached_property
    def version(self):
        """Get current package version"""
        version = metadata.version(self.package_name)
        return {**semver.parse(version), 'raw': version}

    @cached_property
    def router(self):
        """Override this if you want to setup custom swaggerrouter."""
        self.logger.info(f'Setting docs at {self.prefix}docs')
        settings = RapiDocUiSettings(path=f'{self.prefix}docs',
                                     theme="light",
                                     show_header=False,
                                     allow_server_selection=False)
        description = ''
        with suppress(Exception):
            description = metadata.metadata(self.package_name)['Summary']
            description = '\n'.join(
                metadata.metadata(self.package_name).as_string().split(
                    'Description-Content-Type')[1].split('\n')[1:])

        return SwaggerDocs(self.aiohttp_application,
                           title=self.package_name,
                           version=self.version['raw'],
                           description=description,
                           components=self.package_directory / 'openapi.yml',
                           swagger_ui_settings=settings,
                           request_key='payload')

    @property
    def middlewares(self):
        """Setup app middlewares, override this method if you want to add
        custom middlewares.

        This should always return a list, so, in case you need to extend it
        from a subclass, use something like::

            return [YourMiddleware(), *super().middlewares]

        """
        return MetisLogger.get_middlewares(self)

    @property
    def prefix(self):
        """Return an application prefix.

        All routes will be prepend with this.
        Defaults to /package_name/api/v<major_version>/
        """
        app_prefix = self.env('app_prefix', self.package_name)
        return f'/{app_prefix}/api/v{self.version["major"]}/'

    @cached_property
    def aiohttp_application(self):
        """Implement custom app extraction methods."""
        app = aiohttp.web.Application(middlewares=self.middlewares,
                                      debug=self.env('DEBUG', False))

        async def close_aiozipkin(app) -> None:
            if APP_AIOZIPKIN_KEY in app and app[APP_AIOZIPKIN_KEY]:
                await app[APP_AIOZIPKIN_KEY].close()

        app.on_startup.append(HTTPModel.setup)
        app.on_startup.append(MongoModel.setup)
        app.on_cleanup.append(close_aiozipkin)
        app['logger'] = self.logger
        app['application'] = self
        return app

    def add_routes(self, routes):
        """Add route with swagger router."""
        self.router.add_routes([
            aiohttp.web.route(route.method, f'{self.prefix}{route.path}',
                              route.handler, **route.kwargs)
            for route in routes
        ])

    def swagger_spec(self, app):
        """Return complete swagger specifiction as json"""
        return json.dumps(app[_SWAGGER_SPECIFICATION], cls=CustomEncoder)
