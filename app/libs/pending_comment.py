from app.models import PendingComment, comment_actions
from app.libs import comment as commentlib
from app.libs import rejected_comment as rejectedcommentlib
from app.libs import comment_action_log as commentactionloglib


def create(commenter, editors_pick, asset, content, ip_address, parent=0):
    comment = PendingComment.create(
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent
    )
    return comment.id


def get(id):
    pending_comment = PendingComment.select().where(PendingComment.id == id).first()
    return pending_comment.to_dict() if pending_comment else None


def list_(page=1, size=20):
    comments = PendingComment.select().order_by(PendingComment.created).paginate(page, size)
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


def approve(id):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.approved.value,
        actor=0
    )
    return commentlib.create(**pending_comment)


def reject(id, note=''):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.rejected.value,
        actor=0
    )
    return rejectedcommentlib.create(note=note, **pending_comment)


def get_comments_by_asset(asset, parent=0, last_comment=None, limit=None):
    where = [PendingComment.asset == asset, PendingComment.parent == parent]
    if parent == 0:  # Top Level Comments(Latest First)
        if last_comment is not None:
            where.append(PendingComment.id < last_comment)
        order = PendingComment.id.desc()
    else:  # Second Level Comments fetch(Oldest First)
        if last_comment is not None:
            where.append(PendingComment.id > last_comment)
        order = PendingComment.id.asc()

    comments = PendingComment.select().where(*where).order_by(order)
    if limit:
        comments = comments.limit(limit)

    return [comment.to_dict() for comment in comments]
