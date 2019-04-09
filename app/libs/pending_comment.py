from app.models import PendingComment, RejectedComment
from app.libs import comment as commentlib


def create(commenter, editiors_pick, asset, content, parent):
    comment = PendingComment.create(
        commenter=commenter,
        editiors_pick=editiors_pick,
        asset=asset,
        content=content,
        parent=parent
    )
    return comment.id


def get(id):
    pending_comment = PendingComment.select().where(PendingComment.id == id).first()
    return pending_comment.to_dict() if pending_comment else None


def delete(id):
    PendingComment.delete().where(PendingComment.id == id).execute()


def update(id, mod_data):
    updatables = ('editiors_pick', 'content')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    PendingComment.update(**update_dict).where(PendingComment.id == id).execute()


def approve(id):
    pending_comment = get(id)
    delete(id)
    return commentlib.create(**pending_comment)


def reject(id, note=''):
    pending_comment = get(id)
    delete(id)
    rejected_comment = RejectedComment.create(note=note, **pending_comment)
    return rejected_comment.id
