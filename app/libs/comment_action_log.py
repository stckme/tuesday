from app.models import CommentActionLog


def create(comment, action, actor):
    action_log = CommentActionLog.create(
        comment=comment,
        action=action,
        actor=actor
    )
    return action_log.id


def list_(page=1, size=20):
    action_logs = CommentActionLog.select().order_by(CommentActionLog.created.desc()).paginate(page, size)
    return [log.to_dict() for log in action_logs]


def list_by_comment(comment_id, page=1, size=20):
    action_logs = CommentActionLog.select().where(
        CommentActionLog.comment == comment_id
        ).order_by(CommentActionLog.created.desc()
        ).paginate(page, size)
    return [log.to_dict() for log in action_logs]
