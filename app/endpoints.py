import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import app.libs.asset as assetlib
import app.libs.pending_comment as pclib
import app.libs.comment_action_log as actionlog
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
    factory.get('/assets/{id}/comments')(assetlib.get_comments_view)
    factory.get('/assets/{id}/replies')(assetlib.get_replies)
    factory.get('/assets/{id}/meta')(assetlib.get_meta)
    factory.get('/assets/meta')(assetlib.get_assets_meta)

    pc_handlers = (pclib.list_, pclib.create, None, pclib.get, None, None)
    factory.map_resource('/comments/pending/', handlers=pc_handlers)
    factory.post('/comments/pending/{id}/approve')(arlib.approve)
    factory.post('/comments/pending/{id}/reject')(arlib.reject)

    actionlog_handlers = (None, actionlog.create, None, None, None, None)
    factory.map_resource('/actionlog/comments/', handlers=actionlog_handlers)
    factory.get('/actionlog/comments/{comment_id}')(actionlog.list_by_comment)
