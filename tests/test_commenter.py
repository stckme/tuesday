from tests.data import test_commenter
from app.models import setup_db, destroy_db
from app.libs import commenter as commenterlib


class state:
    commenter_id = None



def test_suite_setup():
    destroy_db()
    setup_db()


def test_create():
    state.commenter_id = commenterlib.create(**test_commenter)
    assert state.commenter_id


def test_get():
    commenter = commenterlib.get(state.commenter_id)
    assert commenter["id"] == state.commenter_id
    assert commenter["username"] == "test.user"
    assert test_commenter.items() < commenter.items()


def test_generate_username():
    commenter = commenterlib.get(state.commenter_id)
    username = commenterlib.generate_username(test_commenter["name"])
    assert commenter["username"] != username
    assert username == "test.user1"


def test_update():
    mod_data = {"bio": "new_bio"}
    commenterlib.update(state.commenter_id, mod_data)
    commenter = commenterlib.get(state.commenter_id)
    assert commenter["id"] == state.commenter_id
    assert commenter["bio"] == mod_data["bio"]


def test_delete():
    commenterlib.delete(state.commenter_id)
    commenter = commenterlib.get(state.commenter_id)
    assert commenter is None
