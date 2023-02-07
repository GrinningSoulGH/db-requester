import random
from http import HTTPStatus

from aiohttp import web

from populate_db import get_random_string


def random_handler(request):
    return web.Response(
        text=get_random_string(10), status=random.choice(list(HTTPStatus)).value
    )


def init_func(argv):
    app = web.Application()
    app.add_routes([web.route("*", "/{tail:.*}", random_handler)])
    return app
