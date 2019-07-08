from tests.data import test_commenter
from app.models import setup_db, destroy_db
from app.libs import member as memberlib


class state:
    commenter_id = None


def test_suite_setup():
    destroy_db()
    setup_db()


def test_create():
    state.commenter_id = memberlib.create(**test_commenter)
    assert state.commenter_id


def test_get():
    commenter = memberlib.get(state.commenter_id)
    assert commenter["id"] == state.commenter_id
    assert commenter["username"] == "test.user"


def test_generate_username():
    commenter = memberlib.get(state.commenter_id)
    username = memberlib.generate_username(test_commenter["name"])
    assert commenter["username"] != username
    assert username == "test.user1"


def test_update():
    mod_data = {"bio": "new_bio"}
    memberlib.update(state.commenter_id, **mod_data)
    commenter = memberlib.get(state.commenter_id, ["id", "bio"])
    assert commenter["id"] == state.commenter_id
    assert commenter["bio"] == mod_data["bio"]


def test_delete():
    memberlib.delete(state.commenter_id)
    commenter = memberlib.get(state.commenter_id)
    assert commenter is None
