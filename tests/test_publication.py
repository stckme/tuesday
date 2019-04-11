from tests.data import test_publication
from app.models import setup_db, destroy_db
from app.libs import publication as publicationlib


def test_suite_setup():
    destroy_db()
    setup_db()


def test_create():
    publication_id = publicationlib.create(**test_publication)
    assert publication_id == 1


def test_get():
    publication = publicationlib.get(1)
    assert publication['id'] == 1
    assert test_publication.items() < publication.items()


def test_list_():
    publications = publicationlib.list_()
    assert len(publications) == 1


def test_update():
    mod_data = {'domain': 'publisher.example.com'}
    publicationlib.update(1, mod_data)
    publication = publicationlib.get(1)
    assert publication['id'] == 1
    assert publication['domain'] == mod_data['domain']


def test_delete():
    publicationlib.delete(1)
    publication = publicationlib.get(1)
    assert publication is None
