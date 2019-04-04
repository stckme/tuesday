import datetime

import app.bootstrap

import hug

from app.endpoints import setup_routes


def make_app():

    router = hug.route.API(__name__)
    setup_routes(router)


make_app()
