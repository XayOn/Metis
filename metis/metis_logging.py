import logging
import uuid
import asyncio
from functools import partial

from aiohttp_request import middleware_factory, grequest
from loguru import logger
import sentry_sdk

from sentry_sdk.integrations.aiohttp import AioHttpIntegration
import aiozipkin as az
import aiohttp
from aiozipkin.aiohttp_helpers import (APP_AIOZIPKIN_KEY,
                                       REQUEST_AIOZIPKIN_KEY, middleware_maker)


@aiohttp.web.middleware
async def log_middleware(request, handler):
    """Use standard X-Request-ID header to setup logging

    (see https://stackoverflow.com/questions/25433258/)

    Don't forget to add X-Request-ID to redirect_headers setting

    TODO: Add a catching mechanism based on X-Request-ID to ensure idempotency.
    """
    request['X-Request-ID'] = request.headers.get('X-Request-ID',
                                                  uuid.uuid4().hex)
    request['logger'] = request.app['logger'].bind(
        request_id=request['X-Request-ID'])
    return await handler(request)


class MetisLogger:
    """Metis logging and trazability class.

    Setup all the neccesary logging facilities, such as:

    - Setting up loggers
    - Configure loglevels on aiohttp
    - Setup sentry
    - Setup aiozipkin
    - Add trazability headers

    With aiohttp_request we enable automatic coroutine logging.

    This contradicts twelve-factor's logging section, but it's useful on environments
    """
    @classmethod
    def setup(cls, app):
        """Setup app logging.

        By default it'll:

        - Setup a logfile for debug, json format
        - Setup a logfile for info to error, "human-readable" format
        - Setup a logfile for error+, "human-readable" format
        """
        app.setup_logger(logger)

        class InterceptHandler(logging.Handler):
            def emit(self, record):
                # Get corresponding Loguru level if it exists
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # Find caller from where originated the logged message
                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage())

        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        return logger

    @classmethod
    def get_middlewares(cls, app):
        """Setup all logging related middlewares"""
        if dsn := app.env('SENTRY_DSN', None):
            sentry_sdk.init(dsn=dsn, integrations=[AioHttpIntegration()])

        # middleware_maker(skip_routes=None,
        #                  tracer_key=APP_AIOZIPKIN_KEY,
        #                  request_key=REQUEST_AIOZIPKIN_KEY)
        return [middleware_factory(), log_middleware]


class LoggableTaskMethodsClass:
    """Automatically loggable task class.

    Every method in this class that happens to be a coroutine function will be
    automatically logged using logger calls.
    """
    def __getattribute__(self, name):
        parent = super().__getattribute__(name)
        if asyncio.iscoroutinefunction(parent):
            # Wrap all corotuines in logger
            return Logger(
                parent,
                grequest.app['logger'].bind(model=self.__class__.__name__))
        return super().__getattribute__(name)


class Logger:
    """Magic coroutine object log that allows us to have default logs.

    Usage::

        await Logger(coro) -> Will log a starting and finished call as debug
        await Logger(coro).info -> Will log a starting and finished call as
                                   info, and another one as debug with params
                                   and output
    """
    def __init__(self, func, logger):
        self.logger = CoroLogger(logger)
        self.async_func = func
        self.coroutine = None

    def __await__(self):
        return self.logger.info(self.coroutine).__await__()

    def __call__(self, *args, **kwargs):
        self.coroutine = self.async_func(*args, **kwargs)
        return self

    def __getattr__(self, name):
        if name in ('error', 'info', 'debug', 'exception'):
            return getattr(self.logger, name)(self.coroutine)
        return super().__getattr__(self, name)


class CoroLogger:
    def __init__(self, logger):
        self.logger = logger

    def log(self, level, message, *args, stacklevel=2, **kwargs):
        """Log method drop-in replacement"""
        #: TODO: Add a middleware to setup trazability on extra
        kwargs['extra'] = {
            **kwargs.get('extra', {}),
            **grequest.get('extra', {})
        }
        if asyncio.iscoroutine(message):
            return self.log_async(level, message, *args, **kwargs)
        return getattr(self.logger, level)(message,
                                           *args,
                                           stacklevel=stacklevel,
                                           **kwargs)

    async def log_async(self, level, coro, *args, **kwargs):
        """Log a coroutine start and end"""
        cname = coro.__qualname__
        locals_ = coro.cr_frame.f_locals.items()
        params = {k: v for k, v in locals_ if k != 'self'}
        kwargs = dict(stacklevel=3, extra=dict(params=params))

        #: Do not allow for recursive calls to ourselves.
        if cname == 'CoroLogger.log_async':
            return await coro

        if level != 'debug':
            self.log(level, f'starting_{cname}', stacklevel=3)

        self.log('debug', f'starting_{cname}', *args, **kwargs)
        try:
            result = await coro
        except Exception as exc:
            self.log('exception',
                     f'finished_{cname}',
                     *args,
                     stacklevel=4,
                     extra=dict(status='uncaught_exception'))

            raise

        kwargs['extra']['result'] = result
        if level != 'debug':
            self.log(level, f'finished_{cname}', *args, **kwargs)
        self.log('debug', f'finished_{cname}', stacklevel=3)
        return result

    def __getattr__(self, attr):
        if attr in ('critical', 'exception', 'error', 'warning', 'info',
                    'debug'):
            return partial(self.log, attr)
        return super().__getattr__(attr)
