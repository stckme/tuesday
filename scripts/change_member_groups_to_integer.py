from app.models import Member
from peewee import IntegerField
from playhouse.postgres_ext import ArrayField
from appbase.dbutils import add_column, delete_column, rename_column


def change_member_groups_to_integer():
    field = ArrayField(IntegerField, default=[])
    add_column(Member, 'member_groups', field)
    Member._meta.add_field('member_groups', field)
    for member in Member.select():
        num_groups = []
        for group in member.groups:
                num_groups.append(int(group))
        member.member_groups = num_groups
        member.save()
    delete_column(Member, 'groups')
    rename_column(Member, 'member_groups', 'groups')
