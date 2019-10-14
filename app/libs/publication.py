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


def get_assets(id, after=None, page: int=1, limit: int=20):
    assets = Asset.select().order_by(Asset.created.desc())
    where = [Asset.publication==id]
    if after:
        where.append(Asset.created > arrow.get(after).datetime)
    assets = assets.where(*where).paginate(page, limit)
    return [asset.to_dict() for asset in assets]
get_assets.groups_required = [groups.moderator.value]


def get_assets_with_comment_stats(pub_id, page: int=1, limit: int=20, after=None):
    assets = Asset.select(
            Asset,
            fn.COUNT(PendingComment.id).alias('total_pending_comments')
        ).where(
            Asset.publication == pub_id
        ).join(
            PendingComment, JOIN.LEFT_OUTER
        ).order_by(
            fn.COUNT(PendingComment.id).desc(),
            Asset.created.desc()
        ).group_by(
            Asset.id
        ).paginate(page, limit)

    asset_ids = [asset.id for asset in assets]

    assets_with_rejected_comments_count = RejectedComment.select(
            RejectedComment.asset_id,
            fn.COUNT(RejectedComment.id).alias('total_rejected_comments')
        ).where(
            RejectedComment.asset_id << asset_ids
        ).group_by(RejectedComment.asset_id)
    rejected_comment_counts = {
        asset.asset_id: asset.total_rejected_comments for asset in assets_with_rejected_comments_count
    }

    assets_with_comments_count = Comment.select(
            Comment.asset_id,
            fn.COUNT(Comment.id).alias('total_comments')
        ).where(
            Comment.asset_id << asset_ids
        ).group_by(Comment.asset_id)
    comment_counts = {
        asset.id: asset.total_comments for asset in assets_with_comments_count
    }

    return [
        {
            'comments_count': comment_counts.get(asset.id, 0),
            'pending_comments_count': asset.total_pending_comments,
            'rejected_comments_count': rejected_comment_counts.get(asset.id, 0),
            'commenting_closed': asset.commenting_closed,
            **asset.to_dict()
        }
        for asset in assets
    ]
get_assets_with_comment_stats.groups_required = [groups.moderator.value]
