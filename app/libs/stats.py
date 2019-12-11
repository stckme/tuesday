from peewee import fn, SQL
from app.models import Comment, RejectedComment, Member, groups, Asset, PendingComment
import re
import arrow
from datetime import datetime
import inspect
import sys, types


def total_comments(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    approved, = (count for count, in Comment.select(fn.count(Comment.id)).where(Comment.created >= since).tuples())
    rejected, = (count for count, in RejectedComment.select(fn.count(RejectedComment.id)).where(RejectedComment.created >= since).tuples())
    return {'approved': approved,
            'rejected': rejected,
            'total': approved + rejected}


def total_comments_lastNdays(n=0):
    return total_comments(arrow.utcnow().shift(days=-n).span('day')[0].date())


def monthly_comments_count(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    approved = Comment.select(fn.date_trunc(
        'month', Comment.created), fn.count(Comment.id)).where(Comment.created >= since).group_by(fn.date_trunc(
            'month', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()

    rejected = RejectedComment.select(fn.date_trunc(
        'month', RejectedComment.created), fn.count(RejectedComment.id)).where(RejectedComment.created >= since).group_by(fn.date_trunc(
            'month', RejectedComment.created)).order_by(SQL('date_trunc').asc()).tuples()

    total = zip(approved.tuples(), rejected.tuples())
    return [(m1.date().strftime("%B %Y"), c, rc, (c + rc), round(c * 100 / (c + rc)))for (m1, c), (m2, rc) in total]


def monthly_comments_count_lastNmonths(n=4):
    return monthly_comments_count(arrow.utcnow().shift(months=-n).span('day')[0].date())


def weekly_comments_count(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    approved = Comment.select(fn.date_trunc(
        'week', Comment.created), fn.count(Comment.id)).where(Comment.created >= since).group_by(fn.date_trunc(
            'week', Comment.created)).order_by(SQL('date_trunc').asc())

    rejected = RejectedComment.select(fn.date_trunc(
        'week', RejectedComment.created), fn.count(RejectedComment.id)).where(RejectedComment.created >= since).group_by(fn.date_trunc(
            'week', RejectedComment.created)).order_by(SQL('date_trunc').asc())

    total = zip(approved.tuples(), rejected.tuples())
    return [(w1.date().strftime("%d %B %Y"), c, rc, (c + rc), round(c * 100 / (c + rc))) for (w1, c), (w2, rc) in total]


def weekly_comments_count_lastNweeks(n=4):
    return weekly_comments_count(arrow.utcnow().shift(weeks=-n).span('day')[0].date())


def hourly_comments_count(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    comments = Comment.select(fn.date_part(
        'hour', Comment.created), fn.count(Comment.id)).where(Comment.created >= since).group_by(fn.date_part(
            'hour', Comment.created)).order_by(SQL('date_part').asc()).tuples()
    return [(h, c) for (h, c) in comments]


def hourly_comments_count_lastNdays(n=120):
    return hourly_comments_count(arrow.utcnow().shift(days=-n).span('day')[0].date())


def pending_comments_by_asset():
    pending_comments_by_asset = PendingComment.select(PendingComment.asset_id, fn.count(PendingComment.id)).group_by(PendingComment.asset_id).tuples()
    total_pending = sum([count for asset_id,count in pending_comments_by_asset])
    return {'total_pending': total_pending, 'pending_comments_by_asset': [(Asset.get_by_id(asset_id).url, count) for asset_id, count in pending_comments_by_asset]}


def open_assets():
    open_assets = [asset_url for asset_url, in Asset.select(Asset.url).where(
        Asset.open_till > arrow.utcnow().datetime).tuples()]
    return {'count': len(open_assets), 'open_assets': open_assets}


def weekly_unique_commenters_count(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    weekly_commenters_count = Comment.select(fn.date_trunc(
        'week', Comment.created), fn.count(fn.Distinct(Comment.commenter_id))).where(Comment.created >= since).group_by(fn.date_trunc(
            'week', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()
    return [(w.date().strftime('%d %B %Y'), c) for w, c in weekly_commenters_count]


def weekly_unique_commenters_count_lastNweeks(n=4):
    return weekly_comments_count(arrow.utcnow().shift(weeks=-n).span('day')[0].date())


def monthly_unique_commenters_count(since=None):
    if not since:
        since, = (first_comment_created for first_comment_created, in Comment.select(Comment.created).order_by(Comment.created).limit(1).tuples())
    monthly_commenters_count = Comment.select(fn.date_trunc(
        'month', Comment.created), fn.count(fn.Distinct(Comment.commenter_id))).where(Comment.created >= since).group_by(fn.date_trunc(
            'month', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()
    return [(m.date().strftime("%B %Y"), c) for m, c in monthly_commenters_count]


def monthly_unique_commenters_count_lastNmonths(n=4):
    return monthly_comments_count(arrow.utcnow().shift(months=-n).span('day')[0].date())


def yearly_unique_commenters_count():
    yearly_commenters_count = Comment.select(fn.date_trunc(
        'year', Comment.created), fn.count(fn.Distinct(Comment.commenter_id))).group_by(fn.date_trunc(
            'year', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()
    return [(m.date().strftime("%B %Y"), c) for m, c in yearly_commenters_count]


def curr_week_topN_commenters(n=3):
    curr_week_top10_commenters = Comment.select(fn.date_trunc(
        'week', Comment.created), Comment.commenter_id, fn.count(Comment.id)).group_by(fn.date_trunc(
            'week', Comment.created), Comment.commenter_id).where(Comment.created >= arrow.utcnow().span('week')[0].date()).order_by((SQL('count').desc())).limit(n).tuples()
    return [(Member.get_by_id(commenter).name, count) for w, commenter, count in curr_week_top10_commenters]


def curr_month_topN_commenters(n=3):
    curr_month_top10_commenters = Comment.select(fn.date_trunc(
        'month', Comment.created), Comment.commenter_id, fn.count(Comment.id)).group_by(fn.date_trunc(
            'month', Comment.created), Comment.commenter_id).where(Comment.created >= arrow.utcnow().span('month')[0].date()).order_by((SQL('count').desc())).limit(n).tuples()
    return [(Member.get_by_id(commenter).name, count) for m, commenter, count in curr_month_top10_commenters]


def curr_year_topN_commenters(n=3):
    curr_year_top10_commenters = Comment.select(fn.date_trunc(
        'year', Comment.created), Comment.commenter_id, fn.count(Comment.id)).group_by(fn.date_trunc(
            'year', Comment.created), Comment.commenter_id).where(Comment.created >= arrow.utcnow().span('year')[0].date()).order_by((SQL('count').desc())).limit(n).tuples()
    return [(Member.get_by_id(commenter).name, count) for y, commenter, count in curr_year_top10_commenters]


def monthly_topN_commenters(n=3):
    months = Comment.select(fn.date_trunc(
    'month', Comment.created)).group_by(fn.date_trunc('month', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()
    monthly_top_commenters = []
    output_formatter = lambda mtc: (mtc[0].date().strftime("%B %Y"), Member.get_by_id(mtc[1]).name, mtc[2])
    for month in months:
        monthly_top_commenters.extend(list(map(output_formatter, Comment.select(fn.date_trunc(
        'month', Comment.created), Comment.commenter_id, fn.count(Comment.id)).group_by(fn.date_trunc(
            'month', Comment.created), Comment.commenter_id).where(fn.date_trunc(
        'month', Comment.created) == month).order_by((SQL('date_trunc')), (SQL('count')).desc()).limit(n).tuples())))
    return monthly_top_commenters


def monthly_topN_commented_articles(n=10):
    months = Comment.select(fn.date_trunc(
    'month', Comment.created)).group_by(fn.date_trunc('month', Comment.created)).order_by(SQL('date_trunc').asc()).tuples()
    monthly_top_commented_article = []
    output_formatter = lambda mtc: (mtc[0].date().strftime("%B %Y"), Asset.get_by_id(mtc[1]).url, mtc[2])
    for month in months:
        monthly_top_commented_article.extend(list(map(output_formatter, Comment.select(fn.date_trunc(
        'month', Comment.created), Comment.asset_id, fn.count(Comment.id)).group_by(fn.date_trunc(
            'month', Comment.created), Comment.asset_id).where(fn.date_trunc(
        'month', Comment.created) == month).order_by((SQL('date_trunc')), (SQL('count')).desc()).limit(n).tuples())))
    return monthly_top_commented_article


def last2days_topN_commented_articles(n=10):
    top10_commented_articles_last2days = Comment.select(Comment.asset_id, fn.count(Comment.id)).group_by(Comment.asset_id).where(Comment.created >= arrow.utcnow().shift(days=-2).span('day')[0].date()).order_by((SQL('count')).desc()).limit(n).tuples()
    return [(Asset.get_by_id(asset_id).url, count) for asset_id, count in top10_commented_articles_last2days]


def editors_pick():
    editors_pick_count = 0
    editors_pick_comments_commenter = {}
    for commenter_id, is_editors_pick in Comment.select(Comment.commenter_id, Comment.editors_pick).tuples():
        if is_editors_pick:
            editors_pick_count += 1
            commenter = Member.get_by_id(commenter_id).name
            if commenter in editors_pick_comments_commenter:
                editors_pick_comments_commenter[commenter] += 1
            else:
                editors_pick_comments_commenter[commenter] = 1
    return {'count': editors_pick_count, 'commenters': editors_pick_comments_commenter}


# creates a dict of all the above stats with function name as keys and their return data as values
def get_all_stats():
    is_function_local = lambda object : isinstance(object, types.FunctionType) and object.__module__ == __name__
    data = {stat: getattr(sys.modules[__name__], stat)() for stat, stat_data in inspect.getmembers(sys.modules[__name__], predicate=is_function_local) if stat != 'get_all_stats'}
    return data
