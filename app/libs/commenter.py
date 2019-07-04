from app.models import User, groups
from app.libs import user as userlib


model_common_fields = ['id', 'name', 'username', 'badges']


delete = userlib.delete
generate_username = userlib.generate_username


def create(id, name=None, email=None, username=None, bio=None, web=None):
    return userlib.create(id=id, name=name, email=email, username=username, bio=bio, web=web)


def get(id, fields=None):
    fields = fields or model_common_fields
    return userlib.get(id, fields=fields)


def get_or_create(id, fields=None, user=None):
    fields = fields or model_common_fields
    return userlib.get_or_create(id, fields=fields)


def update(id, **mod_data):
    updatables = ('uid', 'username', 'name', 'enabled', 'badges', 'bio', 'web', 'verified')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    userlib.update(id, **update_dict)


def block(id):
    update(id, enabled=False)
block.groups_required = [groups.moderator.value]
