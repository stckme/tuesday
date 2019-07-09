import arrow
from nose.tools import raises
from app.libs import asset as assetlib
from app.libs import member as memberlib
from app.libs import publication as publicationlib
from app.libs import asset_request as assetrequestlib
from app.models import setup_db, destroy_db, asset_request_statuses
from tests.data import test_commenter, test_publication
from tests.data import test_new_publication_asset_request, test_asset_request, \
    test_asset_request_id, test_new_publication_asset_request_id


def test_suite_setup():
    destroy_db()
    setup_db()
    memberlib.create(**test_commenter)
    publicationlib.create(**test_publication)


def test_create():
    asset_request_id = assetrequestlib.create(**test_asset_request)
    assert asset_request_id == test_asset_request_id
    asset_request = assetrequestlib.get(asset_request_id)
    assert asset_request['status'] == asset_request_statuses.pending.value


def test_get():
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert test_asset_request.items() < asset_request.items()


def test_accept():
    assert not assetlib.exists(test_asset_request_id)

    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert asset_request['status'] == asset_request_statuses.pending.value
    assetrequestlib.approve(test_asset_request_id, approver=12)
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert asset_request['status'] == asset_request_statuses.accepted.value
    asset = assetlib.get(test_asset_request_id)
    assert asset['id'] == test_asset_request_id
    assert asset['url'] == asset_request['url']

    assetlib.stop(asset['id'])
    asset = assetlib.get(test_asset_request_id)
    assert asset['open_till'] < arrow.utcnow().datetime
    assetlib.restart(asset['id'])
    asset = assetlib.get(test_asset_request_id)
    assert asset['open_till'] > arrow.utcnow().datetime


@raises(Exception)
def test_cancel_accepted_request():
    assetrequestlib.cancel(test_asset_request_id, 12)


def test_update():
    mod_data = {'url': 'http://publisher.example.test/12346'}
    assetrequestlib.update(test_asset_request_id, mod_data)
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert asset_request['url'] == mod_data['url']
    assert asset_request['status'] == asset_request_statuses.pending.value


def test_reject():
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert asset_request['status'] == asset_request_statuses.pending.value
    assetrequestlib.reject(test_asset_request_id, approver=12)
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['id'] == test_asset_request_id
    assert asset_request['status'] == asset_request_statuses.rejected.value
    asset = assetlib.get(test_asset_request_id)
    assert asset['id'] == asset_request['id']
    assert asset['url'] != asset_request['url']


def test_cancel_pending():
    assetrequestlib.cancel(test_asset_request_id, 123)
    asset_request = assetrequestlib.get(test_asset_request_id)
    assert asset_request['status'] == asset_request_statuses.cancelled.value


def test_create_with_new_publication():
    asset_request_id = assetrequestlib.create(**test_new_publication_asset_request)
    assert asset_request_id == test_new_publication_asset_request_id
    asset_request = assetrequestlib.get(asset_request_id)
    assert asset_request['status'] == asset_request_statuses.pending.value
