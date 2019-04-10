from app.models import RejectedComment


def create(id, commenter, editors_pick, asset, content, ip_address, parent, created, note):
    comment = RejectedComment.create(
        id=id,
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent,
        created=created,
        note=note
    )
    return comment.id


def get(id):
    comment = RejectedComment.select().where(RejectedComment.id == id).first()
    return comment.to_dict() if comment else None


def get_all(page=1, size=20):
    comments = RejectedComment.select().order_by(RejectedComment.created.desc()).paginate(page, size)
    return [comment.to_dict() for comment in comments]


def exists(id):
    comment = RejectedComment.select().where(RejectedComment.id == id).first()
    return bool(comment)
