from app.libs import commenter as commenterlib


test_commenter = dict(
    uid=1,
    username="tester",
    name="test user",
    bio="I am a tester",
    web="test.scroll.in"
)


def test_create():
    commenter = commenterlib.create(**test_commenter)
    assert commenter.id == 1


def test_get():
    commenter = commenterlib.get(1)
    assert commenter["id"] == 1
    assert test_commenter.items() < commenter.items()


def test_update():
    mod_data = {"id": 3}
    try:
        commenterlib.update(1, mod_data)
    except:
        pass
    else:
        assert False

    mod_data = {"bio": "updated_bio"}
    commenterlib.update(1, mod_data)
    commenter = commenterlib.get(1)
    assert commenter["id"] == 1
    assert commenter["bio"] == mod_data["bio"]


def test_delete():
    commenterlib.delete(1)
    commenter = commenterlib.get(1)
    assert commenter is None
