from tests.data import test_commenter
from app.models import setup_db, destroy_db
from app.libs import commenter as commenterlib


def test_suite_setup():
    destroy_db()
    setup_db()


def test_create():
    commenter_id = commenterlib.create(**test_commenter)
    assert commenter_id == 1


def test_get():
    commenter = commenterlib.get(1)
    assert commenter["id"] == 1
    assert test_commenter.items() < commenter.items()


def test_update():
    mod_data = {"bio": "new_bio"}
    commenterlib.update(1, mod_data)
    commenter = commenterlib.get(1)
    assert commenter["id"] == 1
    assert commenter["bio"] == mod_data["bio"]


def test_delete():
    commenterlib.delete(1)
    commenter = commenterlib.get(1)
    assert commenter is None
