import app.libs.debug as debughelpers


def setup_routes(factory):

    factory.get('/echo/{something}')(debughelpers.echo)
    factory.post('/echo')(debughelpers.echo)
