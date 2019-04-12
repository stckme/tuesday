import arrow

from converge import settings
from app.models import Asset
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


# Todo Cache below method
def get_comments(id, parent=0, last_comment=None, limit=10, children_limit=None):
    # Getting Approved Comments
    approved_comments = commentlib.get_comments_by_asset(
        asset=id, parent=parent, last_comment=last_comment, limit=limit
    )
    if parent == 0:
        approved_comments = map(
            lambda comment: {
                **comment,
                'pending': False,
                'replies': get_comments(id, parent=comment['id'], limit=children_limit)
            },
            approved_comments
        )
    else:
        approved_comments = map(lambda comment: {**comment, 'pending': False}, approved_comments)

    # Getting Pending Comments
    pending_comments = pendingcommentlib.get_comments_by_asset(
        asset=id, parent=parent, last_comment=last_comment, limit=None
    )
    pending_comments = map(lambda comment: {**comment, 'pending': True}, pending_comments)

    # Combining Approved & Pending Comments
    if parent == 0:
        comments = list(pending_comments) + list(approved_comments)
    else:
        comments = list(approved_comments) + list(pending_comments)

    return comments


def get_user_accesible_comments(id, user=None, parent=0, last_comment=None, limit=10, children_limit=None):
    comments = get_comments(
        id, parent=parent, last_comment=last_comment,
        limit=limit, children_limit=children_limit
    )
    user_accessible_comments = []
    for comment in comments:
        if comment['pending'] is False or comment['commenter'] == user:
            comment['replies'] = [
                reply for reply in comment.get('replies', [])
                if reply['pending'] is False or reply['commenter'] == user
            ]
            user_accessible_comments.append(comment)

    return user_accessible_comments
