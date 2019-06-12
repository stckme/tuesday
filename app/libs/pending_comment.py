from apphelpers.rest.hug import user_id

from app.models import PendingComment, comment_actions, User
from app.libs import comment as commentlib
from app.libs import commenter as commenterlib
from app.libs import rejected_comment as rejectedcommentlib
from app.libs import comment_action_log as commentactionloglib


commenter_fields = [User.id, User.username, User.name, User.badges]


def create(commenter_id: user_id, asset, content, editors_pick=False, ip_address=None, parent=0):
    commenter = commenterlib.get_or_create(commenter_id)
    comment = PendingComment.create(
        commenter_id=commenter_id,
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent
    )
    return comment.id
create.groups_forbidden = ['unverified']


def get(id):
    pending_comment = PendingComment.select().where(PendingComment.id == id).first()
    return pending_comment.to_dict() if pending_comment else None


def list_(asset_id=None, page=1, size=20):
    comments = PendingComment.select().order_by(PendingComment.created).paginate(page, size)
    if asset_id:
        comments = comments.where(PendingComment.asset == asset_id)
    return [comment.to_dict() for comment in comments]


def exists(id):
    pending_comment = PendingComment.select().where(PendingComment.id == id).first()
    return bool(pending_comment)


def delete(id):
    PendingComment.delete().where(PendingComment.id == id).execute()


def update(id, mod_data):
    updatables = ('editors_pick', 'content')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    PendingComment.update(**update_dict).where(PendingComment.id == id).execute()
    if update_dict.get('editors_pick'):
        commentactionloglib.create(
            comment=id,
            action=comment_actions.picked.value,
            actor=0
        )


def approve(id, actor: user_id=0):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.approved.value,
        actor=actor
    )
    return commentlib.create(**pending_comment)


def reject(id, note='', actor: user_id=0):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.rejected.value,
        actor=actor
    )
    return rejectedcommentlib.create(note=note, **pending_comment)


def get_replies(parent, limit=None, offset=None):
    where = [PendingComment.parent == parent]
    if offset is not None:
        where.append(PendingComment.id > offset)

    comments = PendingComment.select().where(*where).order_by(PendingComment.id.asc())
    if limit:
        comments = comments.limit(limit)

    return [comment.to_dict() for comment in comments]
