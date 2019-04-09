from app.models import Comment, ArchivedComment


def create(commenter, editiors_pick, asset, content, parent):
    comment = Comment.create(
        commenter=commenter,
        editiors_pick=editiors_pick,
        asset=asset,
        content=content,
        parent=parent
    )
    return comment.id


def get(id):
    comment = Comment.select().where(Comment.id == id).first()
    return comment.to_dict() if comment else None


def delete(id):
    Comment.delete().where(Comment.id == id).execute()


def archive(id):
    comment = get(id)
    delete(id)
    archived_comment = ArchivedComment.create(**comment)
    return archived_comment.id
