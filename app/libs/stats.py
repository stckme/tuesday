from peewee import fn, SQL
from app.models import Comment, RejectedComment, Member, groups, Asset, PendingComment, rejection_reasons
import re
import arrow
from datetime import datetime
import inspect
import sys
import types


# since - datetime object to filter result based on created date
def get_total_comments(since=None):
    approved = Comment.select(Comment.id)
    rejected = RejectedComment.select(RejectedComment.id)
    if since:
        approved = approved.where(Comment.created >= since)
        rejected = rejected.where(RejectedComment.created >= since)
    return {'approved': approved.count(),
            'rejected': rejected.count(),
            'total': approved.count() + rejected.count()}
get_total_comments.groups_required = [groups.moderator.value]
get_total_comments.login_required = True


def get_total_comments_lastNdays(n=0):
    return get_total_comments(arrow.utcnow().shift(days=-int(n)).span('day')[0].date())
get_total_comments_lastNdays.groups_required = [groups.moderator.value]
get_total_comments_lastNdays.login_required = True


def get_monthly_comments_count(since=None):
    approved = Comment.select(fn.date_trunc('month', Comment.created), fn.count(Comment.id))\
        .group_by(fn.date_trunc('month', Comment.created))\
        .order_by(SQL('date_trunc').asc())
    rejected = RejectedComment.select(fn.date_trunc('month', RejectedComment.created), fn.count(RejectedComment.id))\
        .group_by(fn.date_trunc('month', RejectedComment.created))\
        .order_by(SQL('date_trunc').asc())
    if since:
        approved = approved.where(Comment.created >= since)
        rejected = rejected.where(RejectedComment.created >= since)
    total = zip(approved.tuples(), rejected.tuples())
    return [(m1.date().isoformat(), c, rc, (c + rc), round(c * 100 / (c + rc))) for (m1, c), (m2, rc) in total]
get_monthly_comments_count.groups_required = [groups.moderator.value]
get_monthly_comments_count.login_required = True


def get_monthly_comments_count_lastNmonths(n=4):
    return get_monthly_comments_count(arrow.utcnow().shift(months=-int(n)).span('month')[0].date())
get_monthly_comments_count_lastNmonths.groups_required = [groups.moderator.value]
get_monthly_comments_count_lastNmonths.login_required = True


def get_weekly_comments_count(since=None):
    approved = Comment.select(fn.date_trunc('week', Comment.created), fn.count(Comment.id))\
        .group_by(fn.date_trunc('week', Comment.created))\
        .order_by(SQL('date_trunc').asc())
    rejected = RejectedComment.select(fn.date_trunc('week', RejectedComment.created), fn.count(RejectedComment.id))\
        .group_by(fn.date_trunc('week', RejectedComment.created))\
        .order_by(SQL('date_trunc').asc())
    if since:
        approved = approved.where(Comment.created >= since)
        rejected = rejected.where(RejectedComment.created >= since)
    total = zip(approved.tuples(), rejected.tuples())
    return [(w1.date().isoformat(), c, rc, (c + rc), round(c * 100 / (c + rc))) for (w1, c), (w2, rc) in total]
get_weekly_comments_count.groups_required = [groups.moderator.value]
get_weekly_comments_count.login_required = True


def get_weekly_comments_count_lastNweeks(n=4):
    return get_weekly_comments_count(arrow.utcnow().shift(weeks=-int(n)).span('week')[0].date())
get_weekly_comments_count_lastNweeks.groups_required = [groups.moderator.value]
get_weekly_comments_count_lastNweeks.login_required = True


def get_hourly_comments_count(since=None):
    comments = Comment.select(fn.date_part('hour', Comment.created), fn.count(Comment.id))\
        .group_by(fn.date_part('hour', Comment.created))\
        .order_by(SQL('date_part').asc())
    if since:
        comments = comments.where(Comment.created >= since)
    return [(h, c) for (h, c) in comments.tuples()]
get_hourly_comments_count.groups_required = [groups.moderator.value]
get_hourly_comments_count.login_required = True


def get_hourly_comments_count_lastNdays(n=120):
    return get_hourly_comments_count(arrow.utcnow().shift(days=-int(n)).span('day')[0].date())
get_hourly_comments_count_lastNdays.groups_required = [groups.moderator.value]
get_hourly_comments_count_lastNdays.login_required = True


def get_pending_comments_by_asset(since=None):
    pending_comments_by_asset = PendingComment.select(PendingComment.asset_id, fn.count(PendingComment.id))\
        .group_by(PendingComment.asset_id)
    if since:
        pending_comments_by_asset = pending_comments_by_asset.where(
            PendingComment.created >= since)
    total_pending = sum(
        [count for asset_id, count in pending_comments_by_asset.tuples()])
    pending_comments_by_asset = [(Asset.get_by_id(
        asset_id).url, count) for asset_id, count in pending_comments_by_asset.tuples()]
    return {'total_pending': total_pending, 'pending_comments_by_asset': pending_comments_by_asset}
get_pending_comments_by_asset.groups_required = [groups.moderator.value]
get_pending_comments_by_asset.login_required = True


def get_pending_comments_by_asset_lastNdays(n=7):
    return get_pending_comments_by_asset(arrow.utcnow().shift(days=-int(n)).span('day')[0].date())
get_pending_comments_by_asset_lastNdays.groups_required = [groups.moderator.value]
get_pending_comments_by_asset_lastNdays.login_required = True


def get_open_assets():
    open_assets = Asset.select(Asset.url)\
        .where(Asset.open_till > arrow.utcnow().datetime)\
        .tuples()
    open_assets = [asset_url for asset_url, in open_assets]
    return {'count': len(open_assets), 'open_assets': open_assets}
get_open_assets.groups_required = [groups.moderator.value]
get_open_assets.login_required = True


def get_weekly_unique_commenters_count(since=None):
    weekly_commenters_count = Comment.select(fn.date_trunc('week', Comment.created), fn.count(fn.Distinct(Comment.commenter_id)))\
        .group_by(fn.date_trunc('week', Comment.created))\
        .order_by(SQL('date_trunc').asc())
    if since:
        weekly_commenters_count = weekly_commenters_count.where(
            Comment.created >= since)
    return [(w.date().isoformat(), c) for w, c in weekly_commenters_count.tuples()]
get_weekly_unique_commenters_count.groups_required = [groups.moderator.value]
get_weekly_unique_commenters_count.login_required = True


def get_weekly_unique_commenters_count_lastNweeks(n=4):
    return get_weekly_unique_commenters_count(arrow.utcnow().shift(weeks=-int(n)).span('week')[0].date())
get_weekly_unique_commenters_count_lastNweeks.groups_required = [groups.moderator.value]
get_weekly_unique_commenters_count_lastNweeks.login_required = True


def get_monthly_unique_commenters_count(since=None):
    monthly_commenters_count = Comment.select(fn.date_trunc('month', Comment.created), fn.count(fn.Distinct(Comment.commenter_id)))\
        .group_by(fn.date_trunc('month', Comment.created))\
        .order_by(SQL('date_trunc').asc())
    if since:
        monthly_commenters_count = monthly_commenters_count.where(
            Comment.created >= since)
    return [(m.date().isoformat(), c) for m, c in monthly_commenters_count.tuples()]
get_monthly_unique_commenters_count.groups_required = [groups.moderator.value]
get_monthly_unique_commenters_count.login_required = True


def get_monthly_unique_commenters_count_lastNmonths(n=4):
    return get_monthly_unique_commenters_count(arrow.utcnow().shift(months=-int(n)).span('month')[0].date())
get_monthly_unique_commenters_count_lastNmonths.groups_required = [groups.moderator.value]
get_monthly_unique_commenters_count_lastNmonths.login_required = True


def get_yearly_unique_commenters_count():
    yearly_commenters_count = Comment.select(fn.date_trunc('year', Comment.created), fn.count(fn.Distinct(Comment.commenter_id)))\
        .group_by(fn.date_trunc('year', Comment.created))\
        .order_by(SQL('date_trunc').asc())
    return [(m.date().isoformat(), c) for m, c in yearly_commenters_count.tuples()]
get_yearly_unique_commenters_count.groups_required = [groups.moderator.value]
get_yearly_unique_commenters_count.login_required = True


def get_curr_week_top_commenters(top=3):
    curr_week_top_commenters = Comment.select(fn.date_trunc('week', Comment.created), Comment.commenter, fn.count(Comment.id))\
        .group_by(fn.date_trunc('week', Comment.created), Comment.commenter)\
        .where(Comment.created >= arrow.utcnow().span('week')[0].date())\
        .order_by((SQL('count').desc()))\
        .limit(int(top))
    return [(commenter['name'], count) for w, commenter, count in curr_week_top_commenters.tuples()]
get_curr_week_top_commenters.groups_required = [groups.moderator.value]
get_curr_week_top_commenters.login_required = True


def get_curr_month_top_commenters(top=3):
    curr_month_top_commenters = Comment.select(fn.date_trunc('month', Comment.created), Comment.commenter, fn.count(Comment.id))\
        .group_by(fn.date_trunc('month', Comment.created), Comment.commenter)\
        .where(Comment.created >= arrow.utcnow().span('month')[0].date())\
        .order_by((SQL('count').desc()))\
        .limit(int(top))
    return [(commenter['name'], count) for m, commenter, count in curr_month_top_commenters.tuples()]
get_curr_month_top_commenters.groups_required = [groups.moderator.value]
get_curr_month_top_commenters.login_required = True


def get_curr_year_top_commenters(top=3):
    curr_year_top_commenters = Comment.select(fn.date_trunc('year', Comment.created), Comment.commenter, fn.count(Comment.id))\
        .group_by(fn.date_trunc('year', Comment.created), Comment.commenter)\
        .where(Comment.created >= arrow.utcnow().span('year')[0].date())\
        .order_by((SQL('count').desc()))\
        .limit(int(top))
    return [(commenter['name'], count) for y, commenter, count in curr_year_top_commenters.tuples()]
get_curr_year_top_commenters.groups_required = [groups.moderator.value]
get_curr_year_top_commenters.login_required = True


def get_monthly_top_commenters(top=3, since=None):
    monthly_top_commenters = []
    months = Comment.select(fn.date_trunc('month', Comment.created))
    if since:
        months = months.where(Comment.created >= since)
    months = months.group_by(fn.date_trunc('month', Comment.created))\
        .order_by(SQL('date_trunc').asc())\
        .tuples()
    output_formatter = lambda mtc: (mtc[0].date().isoformat(), mtc[1]['name'], mtc[2])
    for month in months:
        monthly_top_commenters.extend(list(map(output_formatter,
                                               Comment.select(fn.date_trunc(
                                                   'month', Comment.created), Comment.commenter, fn.count(Comment.id))
                                               .group_by(fn.date_trunc('month', Comment.created), Comment.commenter)
                                               .where(fn.date_trunc('month', Comment.created) == month)
                                               .order_by((SQL('date_trunc')), (SQL('count')).desc())
                                               .limit(int(top))
                                               .tuples())))
    return monthly_top_commenters
get_monthly_top_commenters.groups_required = [groups.moderator.value]
get_monthly_top_commenters.login_required = True


def get_monthly_top_commenters_lastNmonths(top=3, n=4):
    return get_monthly_top_commenters(top, arrow.utcnow().shift(months=-int(n)).span('month')[0].date())
get_monthly_top_commenters_lastNmonths.groups_required = [groups.moderator.value]
get_monthly_top_commenters_lastNmonths.login_required = True


def get_monthly_top_commented_articles(top=10, since=None):
    monthly_top_commented_article = []
    months = Comment.select(fn.date_trunc('month', Comment.created))
    if since:
        months = months.where(Comment.created >= since)
    months = months.group_by(fn.date_trunc('month', Comment.created))\
        .order_by(SQL('date_trunc').asc())\
        .tuples()
    output_formatter = lambda mtc: (mtc[0].date().isoformat(), Asset.get_by_id(mtc[1]).url, mtc[2])
    for month in months:
        monthly_top_commented_article.extend(list(map(output_formatter,
                                                      Comment.select(fn.date_trunc(
                                                          'month', Comment.created), Comment.asset_id, fn.count(Comment.id))
                                                      .group_by(fn.date_trunc('month', Comment.created), Comment.asset_id)
                                                      .where(fn.date_trunc('month', Comment.created) == month)
                                                      .order_by((SQL('date_trunc')), (SQL('count')).desc())
                                                      .limit(int(top))
                                                      .tuples())))
    return monthly_top_commented_article
get_monthly_top_commented_articles.groups_required = [groups.moderator.value]
get_monthly_top_commented_articles.login_required = True


def get_monthly_top_commented_articles_lastNmonths(top=10, n=4):
    return get_monthly_top_commented_articles(top, arrow.utcnow().shift(months=-int(n)).span('month')[0].date())
get_monthly_top_commented_articles_lastNmonths.groups_required = [groups.moderator.value]
get_monthly_top_commented_articles_lastNmonths.login_required = True


def get_last2days_top_commented_articles(top=10):
    last2days_top_commented_articles = Comment.select(Comment.asset_id, fn.count(Comment.id))\
        .group_by(Comment.asset_id)\
        .where(Comment.created >= arrow.utcnow().shift(days=-int(2)).span('day')[0].date())\
        .order_by((SQL('count')).desc())\
        .limit(int(top))
    return [(Asset.get_by_id(asset_id).url, count) for asset_id, count in last2days_top_commented_articles.tuples()]
get_last2days_top_commented_articles.groups_required = [groups.moderator.value]
get_last2days_top_commented_articles.login_required = True


# returns a dict containing total featured comments and their commenters with individual counts
def get_featured_comments():
    featured_comments = Comment.select(Comment.commenter, fn.count(Comment.id))\
        .group_by(Comment.commenter)\
        .where(Comment.editors_pick == True)\
        .tuples()
    count = sum([count for commenter, count in featured_comments])
    commenters = [(
        commenter['name'], count) for commenter, count in featured_comments]
    return {'count': count, 'commenters': commenters}
get_featured_comments.groups_required = [groups.moderator.value]
get_featured_comments.login_required = True


# returns a dict containing rejected comments count and their commenters categorized by reason
def get_rejected_comments(since=None):
    rejected_comments = {i.name: {} for i in rejection_reasons}
    rejected = RejectedComment.select(RejectedComment.reason, RejectedComment.commenter, fn.count(RejectedComment.id))\
        .group_by(RejectedComment.reason, RejectedComment.commenter)
    if since:
        rejected = rejected.where(RejectedComment.created >= since)
    for reasons in rejected_comments.keys():
        count = sum([count for reason, commenter,
                     count in rejected.tuples() if reason == rejection_reasons[reasons].value])
        commenters = [(commenter['name'], count) for reason, commenter,
                      count in rejected.tuples() if reason == rejection_reasons[reasons].value]
        rejected_comments[reasons]['count'] = count
        rejected_comments[reasons]['commenter'] = commenters
    return rejected_comments
get_rejected_comments.groups_required = [groups.moderator.value]
get_rejected_comments.login_required = True


def get_rejected_comments_lastNmonths(n=4):
    return get_rejected_comments(arrow.utcnow().shift(months=-int(n)).span('month')[0].date())
get_rejected_comments_lastNmonths.groups_required = [groups.moderator.value]
get_rejected_comments_lastNmonths.login_required = True
