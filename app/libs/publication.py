from app.models import Publication, Asset


def create(name, domain):
    publication = Publication.create(name=name, domain=domain)
    return publication.id


def get(id):
    publication = Publication.select().where(Publication.id == id).first()
    return publication.to_dict() if publication else None


def get_by_domain(domain):
    publication = Publication.select().where(Publication.domain == domain).first()
    return publication.to_dict() if publication else None


def list_():
    publications = Publication.select().execute()
    return [publication.to_dict() for publication in publications]


def update(id, mod_data):
    updatables = ('name', 'domain')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    Publication.update(**update_dict).where(Publication.id == id).execute()


def delete(id):
    Publication.delete().where(Publication.id == id).execute()


def get_assets(id):
    assets = Asset.select().where(Asset.publication==id).order_by(Asset.created.desc())
    return [asset.to_dict() for asset in assets]
