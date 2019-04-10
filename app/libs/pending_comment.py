from app.models import PendingComment
from app.libs import comment as commentlib
from app.libs import rejected_comment as rejectedcommentlib


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


def approve(id):
    pending_comment = get(id)
    delete(id)
    return commentlib.create(**pending_comment)


def reject(id, note=''):
    pending_comment = get(id)
    delete(id)
    return rejectedcommentlib.create(note=note, **pending_comment)
