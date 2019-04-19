from app.models import Commenter
from app.libs import commenter_stats as commenterstatslib

from converge import settings


def create(uid, username, name, bio, web):
    commenter = Commenter.create(uid=uid, username=username, name=name, bio=bio, web=web)
    commenterstatslib.create(commenter.id)
    return commenter.id


def get(id):
    commenter = Commenter.select().where(Commenter.id == id).first()
    return commenter.to_dict() if commenter else None


def update(id, mod_data):
    updatables = ('uid', 'username', 'name', 'enabled', 'badges', 'bio', 'web', 'verified')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    Commenter.update(**update_dict).where(Commenter.id == id).execute()


def delete(id):
    Commenter.delete().where(Commenter.id == id).execute()


def calculate_karma(id):
    karma = 0
    stats = commenterstatslib.get(id)
    total_comments = stats['comments'] + stats['rejected']
    if total_comments >= settings.MIN_COMMENTS_REQUIRED_FOR_KARMA:
        karma = 100 * stats['comments'] / total_comments
    return karma
