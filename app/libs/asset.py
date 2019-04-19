import arrow

from converge import settings
from app.models import Asset, PendingComment, Comment
from app.libs import comment as commentlib
from app.libs import pending_comment as pendingcommentlib


def create_or_replace(id, url, publication, open_till=None):
    if open_till is None:
        open_till = arrow.utcnow().shift(days=settings.DEFAULT_ASSET_OPEN_DURATION).datetime
    asset = Asset.create(
        id=id,
        url=url,
        publication=publication,
        open_till=open_till
    )
    return asset.id


def exists(id):
    asset = Asset.select().where(Asset.id == id).first()
    return bool(asset)


def get(id):
    asset = Asset.select().where(Asset.id == id).first()
    return asset.to_dict() if asset else None


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
        if comment['pending'] is False or comment['commenter'] == user_id:
            comment['replies'] = filter_inaccessible_comments(
                user_id, comment.get('replies', []), replies_limit, replies_limit
            )
            user_accessible_comments.append(comment)
            if limit is not None:
                limit -= 1
                if limit == 0:
                    break
    return user_accessible_comments


def get_comments(id, user_id=None, parent=0, offset=None, limit=None, replies_limit=None):
    limit = limit if limit else settings.DEFAULT_COMMENTS_FETCH_LIMIT
    replies_limit = replies_limit if replies_limit else settings.DEFAULT_REPLIES_FETCH_LIMIT

    comments = get_unfiltered_comments(
        id, parent=parent, offset=offset,
        limit=limit, replies_limit=replies_limit
    )
    return filter_inaccessible_comments(user_id, comments, limit, replies_limit)


def get_replies(parent, user_id=None, limit=None, offset=None):
    limit = limit if limit else settings.DEFAULT_COMMENTS_FETCH_LIMIT
    replies = get_unfiltered_replies(parent=parent, limit=limit, offset=offset)
    return filter_inaccessible_comments(user_id, replies, limit, limit)


def get_approved_comments_count(id, offset=None):
    where = [Comment.asset == id]
    if offset is not None:
        where.append(
            (Comment.id < offset) | ((Comment.parent < offset) & (Comment.parent != 0))
        )
    return Comment.select().where(*where).count()


def get_pending_comments_count(id, offset=None, user_id=None):
    where = [PendingComment.asset == id, PendingComment.commenter == user_id]
    if offset is not None:
        where.append(
            (PendingComment.id < offset) |
            ((PendingComment.parent < offset) & (PendingComment.parent != 0))
        )
    return PendingComment.select().where(*where).count()


def get_comments_count(id, offset=None, user_id=None):
    return get_approved_comments_count(id, offset) + get_pending_comments_count(id, offset, user_id)
