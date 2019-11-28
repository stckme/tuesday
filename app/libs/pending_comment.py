from apphelpers.rest.hug import user_id, user_email

from app.models import PendingComment, comment_actions, Member, groups
from app.models import comment_statuses, moderation_policies, rejection_reasons
from app.libs import comment as commentlib
from app.libs import member as memberlib
from app.libs import rejected_comment as rejectedcommentlib
from app.libs import comment_action_log as commentactionloglib
from converge import settings


commenter_fields = [Member.id, Member.username, Member.name, Member.badges]


def should_approve():
    if settings.MODERATION_POLICY == moderation_policies.automatic.value:
        return True
    return False


def create(
        commenter_id: user_id, asset, content, editors_pick=False, ip_address=None,
        parent=0, id=None, created=None):
    commenter = memberlib.get_or_create(commenter_id)
    data = dict(
        commenter_id=commenter_id,
        commenter=commenter,
        editors_pick=editors_pick,
        asset=asset,
        content=content,
        ip_address=ip_address,
        parent=parent
    )
    if id:
        data['id'] = id
    if created:
        data['created'] = created
    comment = PendingComment.create(**data)
    status = comment_statuses.pending.value
    if should_approve():
        status = comment_statuses.approved.value
        approve(comment.id)
    return {'id': comment.id, 'status': status}
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


def update(id, actor: user_id, **mod_data):
    updatables = ('editors_pick', 'content')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    PendingComment.update(**update_dict).where(PendingComment.id == id).execute()
    if update_dict.get('editors_pick'):
        commentactionloglib.create(
            comment=id,
            action=comment_actions.picked.value,
            actor=actor
        )
update.groups_required = [groups.moderator.value]


def approve(id, actor: user_id):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.approved.value,
        actor=actor
    )
    if settings.EMAIL_NOTIFICATION:
        commenter = memberlib.get(pending_comment['commenter_id'])

        comment = pending_comment['content']
        display_comment = comment[:215] + '...' if len(comment) > 215 else comment

        email_info = dict(
            mail_subject='Comment Approved',
            template_name='comment_approved',
            template_data=dict(
                comment=display_comment,
                comment_id=id
            )
        )
        signals.send_notification.send((commenter['email'],), **email_info)
    return commentlib.create(**pending_comment)
approve.groups_required = [groups.moderator.value]


def reject(id, actor: user_id, note='', reason=None):
    pending_comment = get(id)
    delete(id)
    commentactionloglib.create(
        comment=id,
        action=comment_actions.rejected.value,
        actor=actor
    )
    return rejectedcommentlib.create(
        **pending_comment,
        note=note,
        reason=reason or rejection_reasons.other.value
    )
reject.groups_required = [groups.moderator.value]


def get_replies(parent, limit=None, offset=None):
    where = [PendingComment.parent == parent]
    if offset is not None:
        where.append(PendingComment.id > offset)

    comments = PendingComment.select().where(*where).order_by(PendingComment.id.asc())
    if limit:
        comments = comments.limit(limit)

    return [comment.to_dict() for comment in comments]
