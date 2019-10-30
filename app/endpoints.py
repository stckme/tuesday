import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import app.libs.asset as assetlib
import app.libs.pending_comment as pclib
import app.libs.rejected_comment as rclib
import app.libs.comment as commentlib
import app.libs.comment_action_log as actionlog
import app.libs.member as memberlib
import app.libs.publication as publicationlib
import apphelpers.sessions as sessionlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)
    factory.get('/whoami')(sessionlib.whoami)

    factory.get('/assets/{id}/comments/count')(assetlib.get_comments_count)
    factory.get('/assets/{id}/comments')(assetlib.get_comments_view)
    factory.get('/assets/{id}/comments/{comment_id}')(assetlib.get_comment_view)
    factory.get('/assets/{id}/replies')(assetlib.get_replies)
    factory.get('/assets/{id}/meta')(assetlib.get_meta)
    factory.get('/assets/meta')(assetlib.get_assets_meta)

    comment_handlers = (commentlib.list_, None, None, commentlib.get, commentlib.update, None)
    factory.map_resource('/comments/', handlers=comment_handlers)

    factory.get('/publications/{id}/assets')(publicationlib.get_assets)

    pc_handlers = (pclib.list_, pclib.create, None, pclib.get, None, None)
    factory.map_resource('/comments/pending/', handlers=pc_handlers)

    factory.get('/users/me')(memberlib.get_me)
    factory.patch('/users/me')(memberlib.update_me)
