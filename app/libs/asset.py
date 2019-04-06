import arrow

from converge import settings
from app.models import Asset


def create_or_replace(id, url, publication, open_till=None):
    if open_till is None:
        open_till = arrow.utcnow().shift(days=settings.DEFAULT_ASSET_OPEN_DURATION).datetime
    asset = Asset.create(
        id=id,
        url=url,
        publication=publication,
        open_till=open_till
    )
    return asset.id


def exists(id):
    asset = Asset.select().where(Asset.id == id).first()
    return bool(asset)


def get(id):
    asset = Asset.select().where(Asset.id == id).first()
    return asset.to_dict() if asset else None
