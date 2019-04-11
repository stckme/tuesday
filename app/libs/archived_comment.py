from app.models import ArchivedComment


def create(id, commenter, editors_pick, asset, content, ip_address, parent, created):
    comment = ArchivedComment.create(
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
    comment = ArchivedComment.select().where(ArchivedComment.id == id).first()
    return comment.to_dict() if comment else None


def list_(page=1, size=20):
    comments = ArchivedComment.select().order_by(ArchivedComment.created.desc()).paginate(page, size)
    return [comment.to_dict() for comment in comments]


def exists(id):
    comment = ArchivedComment.select().where(ArchivedComment.id == id).first()
    return bool(comment)
