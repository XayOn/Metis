from .app import MetisApplication
from cleo import Command
from abc import abstractmethod
import aiohttp


class ServeCommand(Command):
    """Start listening with aiohttp server.

    start_server
        {--host=0.0.0.0 : Host to listen on}
        {--port=8080 : Port to listen on}
    """
    @abstractmethod
    def get_app(self):
        """Return a MetisApplication instance with added routes."""

    def handle(self):
        """Handle command.

        For a basic usage, just inherit from this Command and override get_app
        method

        Remember to not override the docstring on the class unless you specify
        a valid cleo one and override this handler. For example

        ..code :: python

            class MyCustomStartServerCommand(ServeCommand):
                def get_app(self):
                    '''Return app'''
                    app = MetisApplication('appname')
                    app.aiohttp_application.on_startup.append(setup_something)
                    app.add_routes([web.post('foo', request_handler)])
                    return app

            Note that all models are automatically usable trough env-variables
            configuration of their databases/endpoints
        """
        app = self.get_app()
        host = app.env('HOST', self.option('host'))
        port = app.env.int('PORT', int(self.option('port')))
        aiohttp.web.run_app(app.aiohttp_application, host=host, port=port)
