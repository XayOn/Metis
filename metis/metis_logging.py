import logging
import asyncio

from aiohttp_request import middleware_factory, grequest

from loguru import logger
import sentry_sdk

from sentry_sdk.integrations.aiohttp import AioHttpIntegration
import aiozipkin as az
from aiozipkin.aiohttp_helpers import (APP_AIOZIPKIN_KEY,
                                       REQUEST_AIOZIPKIN_KEY, middleware_maker)

from .magic_logger import Logger


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
        return [middleware_factory()]


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
