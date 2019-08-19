import arrow
from app.models import Publication, Asset, groups


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
list_.groups_required = [groups.moderator.value]


def update(id, mod_data):
    updatables = ('name', 'domain')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    Publication.update(**update_dict).where(Publication.id == id).execute()
update.groups_required = [groups.community_manager.value]


def delete(id):
    Publication.delete().where(Publication.id == id).execute()
delete.groups_required = [groups.community_manager.value]


def get_assets(id, after=None, page: int=1, limit: int=20):
    assets = Asset.select().order_by(Asset.created.desc())
    where = [Asset.publication==id]
    if after:
        where.append(Asset.created > arrow.get(after).datetime)
    else:
        assets = assets.paginate(page, limit)
    assets = assets.where(*where)
    return sorted(
        [
            {
                'comments_count': asset.comments_count,
                'pending_comments_count': asset.pending_comments_count,
                'rejected_comments_count': asset.rejected_comments_count,
                'commenting_closed': asset.commenting_closed,
                **asset.to_dict()
            }
            for asset in assets
        ],
        key=lambda a: (a['pending_comments_count'], a['created']),
        reverse=True
    )
get_assets.groups_required = [groups.moderator.value]
