from app.models import Commenter


def generate_username(name):
    base_username = ".".join(name.lower().split())
    username = base_username
    cnt = 0
    while get_by_username(username):
        cnt += 1
        username = "{}{}".format(base_username, cnt)
    return username


def create(uid, name, bio, web, username=None):
    if username is None:
        username = generate_username(name)
    commenter = Commenter.create(uid=uid, username=username, name=name, bio=bio, web=web)
    return commenter.id


def get(id):
    commenter = Commenter.select().where(Commenter.id == id).first()
    return commenter.to_dict() if commenter else None


def get_by_username(username):
    commenter = Commenter.select().where(Commenter.username == username).first()
    return commenter.to_dict() if commenter else None


def update(id, mod_data):
    updatables = ('uid', 'username', 'name', 'enabled', 'badges', 'bio', 'web', 'verified')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    Commenter.update(**update_dict).where(Commenter.id == id).execute()


def delete(id):
    Commenter.delete().where(Commenter.id == id).execute()
