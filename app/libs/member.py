from apphelpers import sessions
from apphelpers.rest.hug import user_id

from app.models import Member, groups
from app.libs import sso
from converge import settings


Model = Member
model_common_fields = ['id', 'name', 'username', 'groups', 'email']
user_groups_list = [group.value for group in groups]
sessiondb = sessions.SessionDBHandler(dict(
    host=settings.SESSIONSDB_HOST,
    port=settings.SESSIONSDB_PORT,
    password=settings.SESSIONSDB_PASSWD,
    db=settings.SESSIONSDB_NO
))


def generate_username(name):
    base_username = ".".join(name.lower().split())
    username = base_username
    cnt = 0
    while get_by_username(username):
        cnt += 1
        username = "{}{}".format(base_username, cnt)
    return username


def create(id, name=None, email=None, groups=None, username=None, bio=None, web=None):
    if name is None or email is None:
        userinfo = sessiondb.get_for(id)
        email = email or userinfo['email']
        name = name or userinfo['name']
    username = username or generate_username(name)
    groups = groups or []
    user = Member.create(
        id=id, email=email, username=username, name=name,
        groups=groups, bio=bio, web=web
    )
    return user.id


def exists(id):
    return bool(Member.get_or_none(Member.id == id))


def get(id, fields=None):
    fields = fields or model_common_fields
    model_fields = [getattr(Model, field) for field in fields]
    instance = Model.select(*model_fields).where(Model.id == id).first()
    return instance.to_dict() if instance else None


def get_or_create(id, fields=None):
    user = get(id, fields)
    if user is None:
        create(id=id)
        user = get(id, fields)
    return user


def get_by_username(username):
    user = Member.get_or_none(Member.username == username)
    return user.to_dict() if user else None


def get_by_email(email):
    user = Member.get_or_none(Member.email == email)
    if user is None:
        pass
    return user.to_dict() if user else None


def list_():
    users = Member.select()
    return [user.to_dict() for user in users]
list_.groups_required = [groups.moderator.value]


def update(id, **mod_data):
    updatables = ('uid', 'username', 'name', 'enabled', 'badges', 'bio', 'web', 'verified', 'groups')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    Member.update(**update_dict).where(Member.id == id).execute()
    if groups in mod_data:
        sso.update_user_groups(id, mod_data['groups'])
update.groups_required = [groups.moderator.value]


def get_me(id: user_id, fields=None):
    fields = ['username', 'enabled', 'name', 'badges', 'bio', 'web']
    return get(id, fields)
get_me.login_required = True


def update_me(id: user_id, **mod_data):
    updatables = ('username', 'name', 'bio', 'web')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)
    Member.update(**update_dict).where(Member.id == id).execute()
update_me.login_required = True


def delete(id):
    Member.delete().where(Member.id == id).execute()
