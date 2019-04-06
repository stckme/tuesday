from app.libs import asset as assetlib
from app.models import AssetRequest, asset_request_statuses


def create(url, publication, requester):
    asset = AssetRequest.create(
        url=url,
        publication=publication,
        requester=requester
    )
    return asset.id


def get(id):
    asset_request = AssetRequest.select().where(AssetRequest.id == id).first()
    return asset_request.to_dict() if asset_request else None


def update(id, mod_data):
    updatables = ('url', 'requester')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    update_dict['status'] = asset_request_statuses.pending.value
    AssetRequest.update(**update_dict).where(AssetRequest.id == id).execute()


def approve(id, approver, open_till=None):
    mod_data = {'approver': approver, 'status': asset_request_statuses.accepted.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()
    asset_request = get(id)
    assetlib.create_or_replace(
        id=id,
        url=asset_request['url'],
        publication=asset_request['publication'],
        open_till=open_till
    )


def reject(id, approver):
    mod_data = {'approver': approver, 'status': asset_request_statuses.rejected.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()


def cancel(id, approver):
    asset_request = get(id)
    if asset_request['status'] == asset_request_statuses.accepted.value:
        raise Exception('not possible')
    mod_data = {'approver': approver, 'status': asset_request_statuses.cancelled.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()
