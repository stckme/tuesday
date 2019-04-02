import logging

from app.models import Commenter


def create(uid, username, name, bio, web):
    return Commenter.create(uid=uid, username=username, name=name, bio=bio, web=web)


def get(id):
    commenter = Commenter.select().where(Commenter.id == id).first()
    return commenter.to_dict() if commenter else None


def update(id, mod_data):
    updatables = set((
        'uid',
        'username',
        'name',
        'enabled',
        'badges',
        'bio',
        'web',
        'verified'
    ))
    if not updatables.issuperset(mod_data.keys()):
        raise Exception('not possible')

    Commenter.update(**mod_data).where(Commenter.id == id).execute()


def delete(id):
    Commenter.delete().where(Commenter.id == id).execute()
