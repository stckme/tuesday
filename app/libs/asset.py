import arrow
import datetime

from converge import settings
from apphelpers.rest.hug import user_id
from apphelpers.errors import NotFoundError
from app.models import Asset, PendingComment, Comment, Member, groups
from app.libs import comment as commentlib
from app.libs import member as memberlib
from app.libs import pending_comment as pendingcommentlib


commenter_fields = [Member.id, Member.username, Member.name, Member.badges]


def create_or_replace(id, url, title, publication, moderation_policy, open_till=None):
    if open_till is None:
        open_till = arrow.utcnow().shift(days=settings.DEFAULT_ASSET_OPEN_DURATION).datetime
    asset = Asset.create(
        id=id,
        url=url,
        title=title,
        publication=publication,
        open_till=open_till,
        moderation_policy=moderation_policy
    )
    return asset.id


def update(id, **mod_data):
    updatables = ('title', 'open_till', 'moderation_policy')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    Asset.update(**update_dict).where(Asset.id == id).execute()
update.groups_required = [groups.moderator.value]


def exists(id):
    return bool(Asset.get_or_none(Asset.id == id))


def get(id):
    asset = Asset.get_or_none(Asset.id == id)
    if asset:
        return asset.to_dict()


def get_all(ids):
    assets = Asset.select().where(Asset.id << ids)
    return [asset.to_dict() for asset in assets]


def get_by_url(url):
    return Asset.get_or_none(Asset.url == url)


def list_():
    assets = Asset.select().order_by(Asset.created.desc())
    return [
        {
            'comments_count': asset.comments_count,
            'pending_comments_count': asset.pending_comments_count,
            'rejected_comments_count': asset.rejected_comments_count,
            **asset.to_dict()
        }
        for asset in assets
    ]
list_.groups_required = [groups.moderator.value]


def stop(id):
    open_till = arrow.utcnow().datetime
    update(id, open_till=open_till)
stop.groups_required = [groups.moderator.value]


def stop_all():
    open_till = arrow.utcnow().datetime
    Asset.update({'open_till': open_till}).where(Asset.open_till > open_till).execute()
stop_all.groups_required = [groups.moderator.value]


def restart(id, open_till=None):
    if open_till is None:
        open_till = arrow.utcnow().shift(days=settings.DEFAULT_ASSET_OPEN_DURATION).datetime
    update(id, open_till=open_till)
restart.groups_required = [groups.moderator.value]


def get_pending_comments(id, parent=0, offset=None, limit=None):
    where = [PendingComment.asset == id, PendingComment.parent == parent]
    if offset is not None:
        where.append(PendingComment.id < offset)
    comments = PendingComment.select().where(*where).order_by(PendingComment.id.desc())
    if limit:
        comments = comments.limit(limit)

    return [comment.to_dict() for comment in comments]


def get_approved_comments(id, parent=0, offset=None, limit=None):
    where = [Comment.asset == id, Comment.parent == parent]
    if offset is not None:
        where.append(Comment.id < offset)
    comments = Comment.select().where(*where).order_by(Comment.id.desc())
    if limit:
        comments = comments.limit(limit)
    return [comment.to_dict() for comment in comments]


# Todo Add Caching
def get_unfiltered_replies(parent, limit=10, offset=None):
    # Getting Approved Comments
    approved_replies = commentlib.get_replies(parent=parent, limit=limit, offset=offset)
    approved_replies = [
        {
            **comment,
            'pending': False,
            'replies': get_unfiltered_replies(parent=comment['id'], limit=limit)
        }
        for comment in approved_replies
    ]

    # Getting Pending Comments
    pending_replies = pendingcommentlib.get_replies(parent=parent, limit=limit, offset=offset)
    pending_replies = [{**comment, 'pending': True} for comment in pending_replies]

    # Combining Approved & Pending Comments
    return sorted(approved_replies + pending_replies, key=lambda x: x['created'])


# Todo Add Caching
def get_unfiltered_comments(id, parent=0, offset=None, limit=10, replies_limit=None):
    # Getting Approved Comments
    approved_comments = get_approved_comments(id, parent=parent, offset=offset, limit=limit)
    approved_comments = [
        {
            **comment,
            'pending': False,
            'replies': get_unfiltered_replies(parent=comment['id'], limit=replies_limit)
        }
        for comment in approved_comments
    ]

    # Getting Pending Comments
    pending_comments = get_pending_comments(id, parent=parent, offset=offset, limit=limit)
    pending_comments = [{**comment, 'pending': True} for comment in pending_comments]

    # Combining Approved & Pending Comments
    return sorted(pending_comments + approved_comments, key=lambda x: x['created'], reverse=True)


def filter_inaccessible_comments(user_id, comments, limit, replies_limit=None):
    user_accessible_comments = []
    for comment in comments:
        if comment['pending'] is False or comment['commenter']['id'] == user_id:
            comment['replies'] = filter_inaccessible_comments(
                user_id, comment.get('replies', []), replies_limit, replies_limit
            )
            user_accessible_comments.append(comment)
            if limit is not None:
                limit -= 1
                if limit == 0:
                    break
    return user_accessible_comments


def get_comments(id, user_id: user_id=None, parent=0, offset=None, limit=None, replies_limit=None):
    limit = limit if limit else settings.DEFAULT_COMMENTS_FETCH_LIMIT
    replies_limit = replies_limit if replies_limit else settings.DEFAULT_REPLIES_FETCH_LIMIT

    comments = get_unfiltered_comments(
        id, parent=parent, offset=offset,
        limit=limit, replies_limit=replies_limit
    )
    return filter_inaccessible_comments(user_id, comments, limit, replies_limit)


def get_replies(parent, user_id: user_id=None, limit=None, offset=None):
    limit = limit if limit else settings.DEFAULT_COMMENTS_FETCH_LIMIT
    replies = get_unfiltered_replies(parent=parent, limit=limit, offset=offset)
    return filter_inaccessible_comments(user_id, replies, limit, limit)


# Todo Add Caching
def get_approved_comments_count(id):
    return Comment.select().where(Comment.asset == id).count()


def get_pending_comments_count(id):
    return PendingComment.select().where(PendingComment.asset == id).count()


def get_comments_count(id):
    return get_approved_comments_count(id)


def get_comments_view(id, user_id: user_id=None, offset=None, limit: int=None):
    view = {"comments": get_comments(id, user_id, offset=offset, limit=limit)}
    if user_id:  # to support anonymous view
        user = memberlib.get_or_create(user_id, fields=['username', 'enabled', 'name'])
        view["commenter"] = {
            "username": user["username"],
            "banned": not user["enabled"],
            "name": user["name"]
        }

    asset = get(id)
    view["meta"] = {"commenting_closed": asset["open_till"] <= arrow.utcnow().datetime}
    return view


def get_meta(id):
    asset = get(id)
    if asset is not None:
        return {
            'comments_count': get_comments_count(id),
            'commenting_closed': asset["open_till"] <= arrow.utcnow().datetime
        }
get_meta.not_found_on_none = True


def get_assets_meta(ids):
    assets = get_all(ids)
    metas = {
        asset['id']: {
            'comments_count': get_comments_count(asset['id']),
            'commenting_closed': asset['open_till'] <= arrow.utcnow().datetime
        }
        for asset in assets
    }
    return metas


def get_comment_view(id, comment_id, user_id: user_id=None):
    view = {"comment": commentlib.get(comment_id)}

    if user_id:  # to support anonymous view
        user = memberlib.get_or_create(user_id, fields=['username', 'enabled', 'name'])
        view["commenter"] = {
            "username": user["username"],
            "banned": not user["enabled"],
            "name": user["name"]
        }

    asset = get(id)
    view["meta"] = {"commenting_closed": asset["open_till"] <= arrow.utcnow().datetime}
    return view


def list_with_featured_comments(asset_ids, no_of_comments=1):
    assets = Asset.select(
        ).order_by(
            Asset.created.desc()
        ).where(
            (Asset.id << asset_ids) &
            (
                (Asset.open_till > arrow.utcnow().datetime) |
                (Asset.id << (Comment.select(Comment.asset_id)))
            )
        ).execute()
    asset_ids = [asset.id for asset in assets]
    featured_comments = commentlib.get_featured_comments_for_assets(asset_ids, no_of_comments)

    return {
        'assets': [
            {
                'comments_count': asset.comments_count,
                'commenting_closed': asset.commenting_closed,
                'featured_comments': featured_comments.get(asset.id, []),
                **asset.to_dict()
            }
            for asset in assets
        ]
    }
list_.groups_required = [groups.moderator.value]
