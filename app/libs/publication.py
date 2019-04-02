from app.models import Publication


def create(name, host):
    return Publication.create(name=name, host=host)


def get(id):
    publication = Publication.select().where(Publication.id == id).first()
    return publication.to_dict() if publication else None


def get_all():
    publications = Publication.select().execute()
    return [publication.to_dict() for publication in publications]


def update(id, mod_data):
    updatables = set((
        'name',
        'host'
    ))
    if not updatables.issuperset(mod_data.keys()):
        raise Exception('not possible')

    Publication.update(**mod_data).where(Publication.id == id).execute()


def delete(id):
    Publication.delete().where(Publication.id == id).execute()
