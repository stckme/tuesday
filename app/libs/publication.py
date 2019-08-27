import arrow
from peewee import fn, JOIN

from app.models import Publication, Asset, groups
from app.models import PendingComment, RejectedComment, Comment


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


def get_assets(id, page: int=1, limit: int=20):
    assets = Asset.select(
            Asset,
            fn.COUNT(PendingComment.id).alias('total_pending_comments')
        ).where(
            Asset.publication == id
        ).join(
            PendingComment, JOIN.LEFT_OUTER
        ).order_by(
            fn.COUNT(PendingComment.id).desc(),
            Asset.created.desc()
        ).group_by(
            Asset.id
        ).paginate(page, limit)
    asset_ids = [assets.id for assets in assets]

    assets_with_rejected_comments_count = RejectedComment.select(
            RejectedComment.asset_id,
            fn.COUNT(RejectedComment.id).alias('total_rejected_comments')
        ).where(
            RejectedComment.asset_id << asset_ids
        ).group_by(RejectedComment.asset_id)
    rejected_comments_count = {
        asset.asset_id: asset.total_rejected_comments for asset in assets_with_rejected_comments_count
    }

    assets_with_comments_count = Comment.select(
            Comment.asset_id,
            fn.COUNT(Comment.id).alias('total_comments')
        ).where(
            Comment.asset_id << asset_ids
        ).group_by(Comment.asset_id)
    comments_count = {
        asset.id: asset.total_comments for asset in assets_with_comments_count
    }
    return [
        {
            'comments_count': comments_count.get(asset.id, 0),
            'pending_comments_count': asset.total_pending_comments,
            'rejected_comments_count': rejected_comments_count.get(asset.id, 0),
            'commenting_closed': asset.commenting_closed,
            **asset.to_dict()
        }
        for asset in assets
    ]
get_assets.groups_required = [groups.moderator.value]
