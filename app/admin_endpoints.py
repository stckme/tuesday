import app.libs.debug as debughelpers
import app.libs.asset_request as arlib
import app.libs.asset as assetlib
import app.libs.pending_comment as pclib
import app.libs.rejected_comment as rclib
import app.libs.comment as commentlib
import app.libs.comment_action_log as actionlog
import app.libs.member as memberlib
import app.libs.publication as publicationlib
import app.libs.stats as statslib
import apphelpers.sessions as sessionlib


def setup_routes(factory):

    factory.get('/echo/{word}')(debughelpers.echo)
    factory.get('/whoami')(sessionlib.whoami)

    ar_handlers = (arlib.list_, arlib.create, None, arlib.get, arlib.update, None)
    factory.map_resource('/assetrequests/', handlers=ar_handlers)
    factory.post('/assetrequests/{id}/approve')(arlib.approve)
    factory.post('/assetrequests/{id}/reject')(arlib.reject)
    factory.post('/assetrequests/{id}/cancel')(arlib.cancel)

    asset_handlers = (assetlib.list_, arlib.create_and_approve, None, assetlib.get, None, None)
    factory.map_resource('/assets/', handlers=asset_handlers)
    factory.get('/assets/{id}/comments/count')(assetlib.get_comments_count)
    factory.get('/assets/{id}/replies')(assetlib.get_replies)
    factory.get('/assets/{id}/meta')(assetlib.get_meta)
    factory.get('/assets/meta')(assetlib.get_assets_meta)
    factory.get('/assets/{id}/comments')(assetlib.get_unfiltered_comments_view)
    factory.get('/assets/{id}/comments/{comment_id}')(assetlib.get_comment_view)
    factory.get('/assets/comments/featured')(assetlib.get_with_featured_comments)

    comment_handlers = (commentlib.list_, None, None, commentlib.get, commentlib.update, None)
    factory.map_resource('/comments/', handlers=comment_handlers)

    actionlog_handlers = (None, actionlog.create, None, None, None, None)
    factory.map_resource('/actionlog/comments/', handlers=actionlog_handlers)
    factory.get('/actionlog/comments/{comment_id}')(actionlog.list_by_comment)

    factory.get('/publications/')(publicationlib.list_)
    factory.get('/publications/{id}/assets')(publicationlib.get_assets_with_comment_stats)

    pc_handlers = (pclib.list_, None, None, pclib.get, None, None)
    factory.map_resource('/comments/pending/', handlers=pc_handlers)

    factory.post('/comments/pending/{id}/approve')(pclib.approve)
    factory.post('/comments/pending/{id}/reject')(pclib.reject)
    factory.get('/comments/rejected/')(rclib.list_)
    factory.post('/comments/rejected/{id}/revert')(rclib.revert)
    factory.post('/comments/rejected/{id}/approve')(rclib.approve)
    factory.post('/comments/approved/{id}/reject')(commentlib.reject)

    member_handlers = (memberlib.list_, None, None, None, memberlib.update, None)
    factory.map_resource('/users/', handlers=member_handlers)

    factory.post('/assets/{id}/stop')(assetlib.stop)
    factory.post('/assets/{id}/restart')(assetlib.restart)

    # Routes for comments stats
    factory.get('/all')(statslib.get_all_stats)
    factory.get('/comments/count/total')(statslib.total_comments)
    factory.get('/comments/count/lastndays/{n}')(statslib.total_comments_lastNdays)
    factory.get('/comments/count/monthly')(statslib.monthly_comments_count)
    factory.get('/comments/count/monthly/lastnmonths/{n}')(statslib.monthly_comments_count_lastNmonths)
    factory.get('/comments/count/weekly')(statslib.weekly_comments_count)
    factory.get('/comments/count/weekly/lastnweeks/{n}')(statslib.weekly_comments_count_lastNweeks)
    factory.get('/comments/count/hourly')(statslib.hourly_comments_count)
    factory.get('/comments/count/hourly/lastndays/{n}')(statslib.hourly_comments_count_lastNdays)
    factory.get('/commenters/count/weekly')(statslib.weekly_unique_commenters_count)
    factory.get('/commenters/count/weekly/lastnweeks/{n}')(statslib.weekly_unique_commenters_count_lastNweeks)
    factory.get('/commenters/count/monthly')(statslib.monthly_unique_commenters_count)
    factory.get('/commenters/count/monthly/lastnmonths/{n}')(statslib.monthly_unique_commenters_count_lastNmonths)
    factory.get('/commenters/count/yearly')(statslib.yearly_unique_commenters_count)
    factory.get('/commenters/count/currentweek/top/{n}')(statslib.curr_week_topN_commenters)
    factory.get('/commenters/count/currentmonth/top/{n}')(statslib.curr_month_topN_commenters)
    factory.get('/commenters/count/currentyear/top/{n}')(statslib.curr_year_topN_commenters)
    factory.get('/commenters/count/monthly/top/{n}')(statslib.monthly_topN_commenters)
    factory.get('/assets/comments/count/monthly/top/{n}')(statslib.monthly_topN_commented_articles)
    factory.get('/assets/comments/count/last2days/top/{n}')(statslib.last2days_topN_commented_articles)
    factory.get('/assets/open')(statslib.open_assets)
    factory.get('/comments/pending')(statslib.pending_comments_by_asset)
    factory.get('/commenters/editorspick')(statslib.editors_pick)
