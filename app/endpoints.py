import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import apphelpers.sessions as sessionlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)
    factory.get('/whoami')(sessionlib.whoami)

    ar_handlers = (None, arlib.create, None, arlib.get, arlib.update, None)
    factory.map_resource('/assets/', handlers=ar_handlers)
