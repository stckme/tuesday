import app.bootstrap

import hug

from apphelpers.rest.hug import APIFactory
from app.endpoints import setup_routes

import app.models


def make_app():
    router = hug.route.API(__name__)

    api_factory = APIFactory(router)
    api_factory.setup_db_transaction(app.models.db)

    setup_routes(api_factory)


make_app()
