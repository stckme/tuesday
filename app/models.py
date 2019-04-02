from enum import Enum

from peewee import ForeignKeyField, BooleanField, TextField, IntegerField, DateTimeField
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from apphelpers.db import create_pgdb_pool, create_base_model, created

import settings

db = create_pgdb_pool(database=settings.DB_NAME)
BaseModel = create_base_model(db)


class CommonModel(BaseModel):
    created = created()


class Commenter(CommonModel):
    uid = IntegerField(index=True, unique=True)
    username = TextField(unique=True)
    name = TextField()
    enabled = BooleanField(default=True)
    badges = ArrayField(default=[])
    bio = TextField()
    web = TextField()
    verified = BooleanField(default=False)


class Publication(CommonModel):
    name = TextField(null=False)
    host = TextField(null=False)


class Asset(CommonModel):
    url = TextField()
    publication = ForeignKeyField(Publication, null=True)
    open_till = DateTimeField()


class BaseComment(CommonModel):
    commenter = ForeignKeyField(Commenter, index=True)
    editors_pick = BooleanField(default=False, index=True)
    asset = ForeignKeyField(Asset, index=True, unique=True)
    content = TextField()
    parent = IntegerField(default=0, null=False)
    ip_address = TextField()


class PendingComment(BaseComment):
    pass


class Comment(BaseComment):
    pass


class RejectedComment(BaseComment):
    note = TextField()


class ArchivedComment(BaseComment):
    pass


class CommenterStats(CommonModel):
    # {count: 0, reported: <int>, accepted: <int>, rejected: <int>}
    commenter = ForeignKeyField(Commenter, index=True)
    comments = IntegerField(default={})
    reported = IntegerField(default={})
    editor_picks = IntegerField(default=0)


class AssetRequest(CommonModel):
    url = TextField(Asset)
    requester = IntegerField(null=True)
    approver = IntegerField(null=True)
    status = IntegerField(default=0)  # 0: pending, 1: accepted, 2: rejected


class FlaggedReport(CommonModel):
    """
    A genuine comment can be flagged
    Keeping flag records in separate table ensures
        - flagging abuse doesn't slow down the system and moderation
        - lets track abusers independently
    """
    comment = ForeignKeyField(Commenter, null=False)
    reporter = ForeignKeyField(Commenter, null=False)
    accepted = BooleanField(default=False)


class actions(Enum):
    approved = 0
    rejected = 1
    picked = 2


class CommentActionLog:
    comment = IntegerField(null=False, unique=True)
    actions = BinaryJSONField(default={})
    # actions: {t1: {actor: <int>, action: <int:action-id>}, t2: {actor: ..},..}
    #   actor: <int> # 0 is reserved for system

# Setup helpers

the_models = BaseModel.__subclasses__() + CommonModel.__subclasses__()


def setup_db():
    db.create_tables(the_models, fail_silently=True)


def destroy_db():
    for o in the_models[::-1]:
        if o.table_exists():
            o.drop_table()
            print('DROP: ' + o._meta.name)
