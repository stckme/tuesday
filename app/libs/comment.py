from app.models import Comment
from app.libs import archived_comment as archivedcommentlib


def create(id, commenter, editors_pick, asset, content, ip_address, parent, created):
    comment = Comment.create(
        id=id,
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent,
        created=created
    )
    return comment.id


def get(id):
    comment = Comment.select().where(Comment.id == id).first()
    return comment.to_dict() if comment else None


def get_all(page=1, size=20):
    comments = Comment.select().order_by(Comment.created.desc()).paginate(page, size)
    return [comment.to_dict() for comment in comments]


def update(id, mod_data):
    updatables = ('editors_pick',)
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    Comment.update(**update_dict).where(Comment.id == id).execute()


def exists(id):
    comment = Comment.select().where(Comment.id == id).first()
    return bool(comment)


def delete(id):
    Comment.delete().where(Comment.id == id).execute()


def archive(id):
    comment = get(id)
    delete(id)
    return archivedcommentlib.create(**comment)
