import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import app.libs.asset as assetlib
import app.libs.pending_comment as pclib
import app.libs.rejected_comment as rclib
import app.libs.comment as commentlib
import app.libs.comment_action_log as actionlog
import app.libs.commenter as commenterlib
import app.libs.publication as publicationlib
import apphelpers.sessions as sessionlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)
    factory.get('/whoami')(sessionlib.whoami)

    ar_handlers = (arlib.list_, arlib.create, None, arlib.get, arlib.update, None)
    factory.map_resource('/assetrequests/', handlers=ar_handlers)
    factory.post('/assetrequests/{id}/approve')(arlib.approve)

    asset_handlers = (assetlib.list_, None, None, assetlib.get, None, None)
    factory.map_resource('/assets/', handlers=asset_handlers)
    factory.get('/assets/{id}/comments/count')(assetlib.get_comments_count)
    factory.get('/assets/{id}/comments')(assetlib.get_comments_view)
    factory.get('/assets/{id}/replies')(assetlib.get_replies)
    factory.get('/assets/{id}/meta')(assetlib.get_meta)
    factory.get('/assets/meta')(assetlib.get_assets_meta)

    factory.get('/comments/')(commentlib.list_)
    factory.get('/comments/{id}')(commentlib.get)

    actionlog_handlers = (None, actionlog.create, None, None, None, None)
    factory.map_resource('/actionlog/comments/', handlers=actionlog_handlers)
    factory.get('/actionlog/comments/{comment_id}')(actionlog.list_by_comment)

    # Admin APIs
    factory.get('/publications/')(publicationlib.list_)
    factory.get('/publications/{id}/assets')(publicationlib.get_assets)

    pc_handlers = (pclib.list_, pclib.create, None, pclib.get, None, None)
    factory.map_resource('/comments/pending/', handlers=pc_handlers)

    factory.post('/comments/pending/{id}/approve')(pclib.approve)

    factory.post('/comments/pending/{id}/reject')(pclib.reject)
    factory.get('/comments/rejected/')(rclib.list_)
    factory.post('/comments/rejected/{id}/revert')(rclib.revert)

    factory.post('/commenters/{id}/block')(commenterlib.block)
