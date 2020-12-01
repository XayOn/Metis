from cleo import Application
from .cli import ServeCommand


def main():
    app = Application()
    app.add(ServeCommand())
    app.run()
