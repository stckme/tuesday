import hug

from apphelpers.rest.hug import user_id

from app.models import Comment, comment_actions, Commenter
from app.libs import archived_comment as archivedcommentlib
from app.libs import comment_action_log as commentactionloglib


Model = Comment
model_common_fields = ['id', 'editors_pick', 'asset', 'content',
                         'parent', 'created', 'commenter']
commenter_fields = [Commenter.id, Commenter.username, Commenter.name, Commenter.badges]


def create(id, commenter_id: user_id, commenter, editors_pick, asset, content, ip_address, parent, created):
    comment = Comment.create(
        id=id,
        commenter_id=commenter_id,
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent,
        created=created
    )
    return comment.id


def get(id, fields=None):
    fields = fields or model_common_fields
    model_fields = [getattr(Model, field) for field in fields]
    instance = Model.select(*model_fields).where(Model.id == id).first()
    return instance.to_dict() if instance else None


def list_(asset_id=None, editors_pick: hug.types.smart_boolean=None, page=1, size=20):
    comments = Comment.select().order_by(Comment.created.desc()).paginate(page, size)
    where = []
    if asset_id:
        where.append(Comment.asset == asset_id)
    if editors_pick is not None:
        where.append(Comment.editors_pick == editors_pick)
    if where:
        comments = comments.where(*where)
    return [comment.to_dict() for comment in comments]


def update(id, mod_data):
    updatables = ('editors_pick',)
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    Comment.update(**update_dict).where(Comment.id == id).execute()
    if update_dict.get('editors_pick'):
        commentactionloglib.create(
            comment=id,
            action=comment_actions.picked.value,
            actor=0
        )


def exists(id):
    comment = Comment.select().where(Comment.id == id).first()
    return bool(comment)


def delete(id):
    Comment.delete().where(Comment.id == id).execute()


def archive(id):
    comment = get(id, model_common_fields+['created', 'commenter_id'])
    delete(id)
    return archivedcommentlib.create(**comment)


def get_replies(parent, limit=None, offset=None):
    where = [Comment.parent == parent]
    if offset is not None:
        where.append(Comment.id > offset)

    comments = Comment.select().where(*where).order_by(Comment.id.asc())
    if limit:
        comments = comments.limit(limit)

    return [comment.to_dict() for comment in comments]
