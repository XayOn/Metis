from . import handlers


def setup_routes(app):
    """Setup app handlers."""
    app.router.add_get('/status', handlers.status, name='global_status')
