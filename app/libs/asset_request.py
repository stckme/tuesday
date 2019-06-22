import re
import requests
from hashlib import sha1
from urllib.parse import urlsplit

from apphelpers.rest.hug import user_id
from app.libs import asset as assetlib
from app.libs import publication as publicationlib
from app.models import AssetRequest, asset_request_statuses, moderation_policies, groups


def create(url, title, requester: user_id):
    domain = urlsplit(url).netloc
    publication = publicationlib.get_by_domain(domain)
    if publication is None:
        publication_id = publicationlib.create(name=domain, domain=domain)
    else:
        publication_id = publication['id']
    # asset ids are hashes generated from URLs. Idea is client doesn't need to
    # query server to find id for certain asset. Client can generate the id
    # itself from the asset url (provided it knows the hashing technique used)
    asset = AssetRequest.create(
        id=sha1(bytes(url, 'utf8')).hexdigest(),
        url=url,
        title=title,
        publication=publication_id,
        requester=requester
    )
    return asset.id
create.login_required = True


def get(id):
    asset_request = AssetRequest.select().where(AssetRequest.id == id).first()
    return asset_request.to_dict() if asset_request else None


def list_(page=1, size=20):
    asset_requests = AssetRequest.select().order_by(AssetRequest.created).paginate(page, size)
    return [asset_request.to_dict() for asset_request in asset_requests]


def update(id, mod_data):
    updatables = ('url', 'requester')
    update_dict = dict((k, v) for (k, v) in list(mod_data.items()) if k in updatables)

    update_dict['status'] = asset_request_statuses.pending.value
    AssetRequest.update(**update_dict).where(AssetRequest.id == id).execute()


def approve(id, approver: user_id, open_till=None, moderation_policy=None):
    mod_data = {'approver': approver, 'status': asset_request_statuses.accepted.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()
    asset_request = get(id)
    assetlib.create_or_replace(
        id=id,
        url=asset_request['url'],
        title=asset_request['title'],
        publication=asset_request['publication'],
        moderation_policy=moderation_policy or moderation_policies.default.value,
        open_till=open_till
    )
approve.groups_required = [groups.moderator.value, groups.admin.value]


def reject(id, approver):
    mod_data = {'approver': approver, 'status': asset_request_statuses.rejected.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()
reject.groups_required = [groups.moderator.value, groups.admin.value]


def cancel(id, approver):
    asset_request = get(id)
    if asset_request['status'] == asset_request_statuses.accepted.value:
        raise Exception('not possible')
    mod_data = {'approver': approver, 'status': asset_request_statuses.cancelled.value}
    AssetRequest.update(**mod_data).where(AssetRequest.id == id).execute()
cancel.groups_required = [groups.moderator.value, groups.admin.value]
