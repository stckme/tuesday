from app.libs import publication as publicationlib


test_publication = dict(
    name='Scroll Media',
    host='scroll.in'
)


def test_create():
    publication = publicationlib.create(**test_publication)
    assert publication.id == 1


def test_get():
    publication = publicationlib.get(1)
    assert publication['id'] == 1
    assert test_publication.items() < publication.items()


def test_get_all():
    publications = publicationlib.get_all()
    assert len(publications) == 1


def test_update():
    mod_data = {'id': 3}
    try:
        publicationlib.update(1, mod_data)
    except:
        pass
    else:
        assert False

    mod_data = {'host': 'scroll.team'}
    publicationlib.update(1, mod_data)
    publication = publicationlib.get(1)
    assert publication['id'] == 1
    assert publication['host'] == mod_data['host']


def test_delete():
    publicationlib.delete(1)
    publication = publicationlib.get(1)
    assert publication is None
