import asyncio
from functools import partial
from aiohttp_request import grequest


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
