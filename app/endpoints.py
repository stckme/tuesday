import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import app.libs.asset as assetlib
import app.libs.pending_comment as pendingcommentlib
import apphelpers.sessions as sessionlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)
    factory.get('/whoami')(sessionlib.whoami)

    ar_handlers = (None, arlib.create, None, arlib.get, arlib.update, None)
    factory.map_resource('/assetrequests/', handlers=ar_handlers)
    factory.post('/assetrequests/{id}/approve')(arlib.approve)

    asset_handlers = (None, None, None, assetlib.get, None, None)
    factory.map_resource('/assets/', handlers=asset_handlers)
    factory.get('/assets/{id}/comments/count')(assetlib.get_comments_count)

    comment_handlers = (assetlib.get_comments_view, pendingcommentlib.create, None, None, None, None)
    factory.map_resource('/assets/{id}/comments', handlers=comment_handlers)
