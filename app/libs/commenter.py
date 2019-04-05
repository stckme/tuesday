from app.models import Commenter


def create(uid, username, name, bio, web):
    commenter = Commenter.create(uid=uid, username=username, name=name, bio=bio, web=web)
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
