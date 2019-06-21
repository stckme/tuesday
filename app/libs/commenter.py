from app.models import User, groups
from app.libs import sso


Model = User
model_common_fields = ['id', 'name', 'username', 'badges']
user_groups_list = [group.value for group in groups]


def generate_username(name):
    base_username = ".".join(name.lower().split())
    username = base_username
    cnt = 0
    while get_by_username(username):
        cnt += 1
        username = "{}{}".format(base_username, cnt)
    return username


def create(id, name, bio=None, web=None, username=None):
    if not username:
        username = generate_username(name)
    commenter = User.create(id=id, username=username, name=name, bio=bio, web=web)
    return commenter.id


def exists(id):
    return bool(User.get_or_none(User.id == id))


def get(id, fields=None):
    fields = fields or model_common_fields
    model_fields = [getattr(Model, field) for field in fields]
    instance = Model.select(*model_fields).where(Model.id == id).first()
    return instance.to_dict() if instance else None


def get_or_create(id, fields=None, user_name=None):
    commenter = get(id, fields)
    if commenter is None:
        create(id=id, name=user_name)
        commenter = get(id, fields)
    return commenter


def get_by_username(username):
    commenter = User.get_or_none(User.username == username)
    return commenter.to_dict() if commenter else None


def update(id, **mod_data):
    updatables = ('uid', 'username', 'name', 'enabled', 'badges', 'bio', 'web', 'verified', 'groups')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    User.update(**update_dict).where(User.id == id).execute()
    if groups in mod_data:
        sso.update_user_groups(id, mod_data['groups'])


def delete(id):
    User.delete().where(User.id == id).execute()


def block(id):
    update(id, enabled=False)
