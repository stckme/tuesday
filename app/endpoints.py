import app.libs.debug as debughelpers
import app.libs.asset_request as arlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)

    ar_handlers = (None, arlib.create, None, arlib.get, arlib.update, None)
    factory.map_resource('/resttest/', handlers=ar_handlers)
