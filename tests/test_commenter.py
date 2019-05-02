from tests.data import test_commenter
from app.models import setup_db, destroy_db
from app.libs import commenter as commenterlib

commenter_id = None

def test_suite_setup():
    destroy_db()
    setup_db()


def test_create():
    global commenter_id
    commenter_id = commenterlib.create(**test_commenter)
    assert commenter_id


def test_get():
    commenter = commenterlib.get(commenter_id)
    assert commenter["id"] == commenter_id
    assert commenter["username"] == "test.user"
    assert test_commenter.items() < commenter.items()


def test_generate_username():
    commenter = commenterlib.get(commenter_id)
    username = commenterlib.generate_username(test_commenter["name"])
    assert commenter["username"] != username
    assert username == "test.user1"


def test_update():
    mod_data = {"bio": "new_bio"}
    commenterlib.update(commenter_id, mod_data)
    commenter = commenterlib.get(commenter_id)
    assert commenter["id"] == commenter_id
    assert commenter["bio"] == mod_data["bio"]


def test_delete():
    commenterlib.delete(commenter_id)
    commenter = commenterlib.get(commenter_id)
    assert commenter is None
