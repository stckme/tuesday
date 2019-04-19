from app.models import CommenterStats


def create(commenter_id):
    commenter_stats = CommenterStats.create(commenter=commenter_id)
    return commenter_stats.id


def get(commenter_id):
    commenter = CommenterStats.select().where(CommenterStats.commenter == commenter_id).first()
    return commenter.to_dict() if commenter else None


def update(commenter_id, mod_data):
    updatables = ('comments', 'reported', 'rejected', 'editor_picks')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    CommenterStats.update(**update_dict).where(CommenterStats.commenter == commenter_id).execute()


def increase_comments_count(commenter_id):
    update(commenter_id, {'comments': CommenterStats.comments + 1})


def decrease_comments_count(commenter_id):
    update(commenter_id, {'comments': CommenterStats.comments - 1})


def increase_rejected_count(commenter_id):
    update(commenter_id, {'rejected': CommenterStats.rejected + 1})


def decrease_rejected_count(commenter_id):
    update(commenter_id, {'rejected': CommenterStats.rejected - 1})


def increase_reported_count(commenter_id):
    update(commenter_id, {'reported': CommenterStats.reported + 1})


def decrease_reported_count(commenter_id):
    update(commenter_id, {'reported': CommenterStats.reported - 1})


def increase_editor_picks_count(commenter_id):
    print("(((", commenter_id)
    update(commenter_id, {'editor_picks': CommenterStats.editor_picks + 1})


def decrease_editor_picks_count(commenter_id):
    update(commenter_id, {'editor_picks': CommenterStats.editor_picks - 1})
