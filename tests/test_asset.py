from nose.tools import raises
from app.libs import asset as assetlib
from app.libs import commenter as commenterlib
from app.libs import publication as publicationlib
from app.libs import asset_request as assetrequestlib
from app.models import setup_db, destroy_db, asset_request_statuses
from tests.data import test_commenter, test_publication, test_asset_request


def test_suite_setup():
    destroy_db()
    setup_db()
    commenterlib.create(**test_commenter)
    publicationlib.create(**test_publication)


def test_create():
    asset_request_id = assetrequestlib.create(**test_asset_request)
    assert asset_request_id == 1
    asset_request = assetrequestlib.get(asset_request_id)
    assert asset_request['status'] == asset_request_statuses.pending.value


def test_get():
    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert test_asset_request.items() < asset_request.items()


def test_accept():
    assert not assetlib.exists(1)

    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert asset_request['status'] == asset_request_statuses.pending.value
    assetrequestlib.approve(1, approver=12)
    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert asset_request['status'] == asset_request_statuses.accepted.value
    asset = assetlib.get(1)
    assert asset['id'] == asset_request['id']
    assert asset['url'] == asset_request['url']


@raises(Exception)
def test_cancel_accepted_request():
    assetrequestlib.cancel(1)


def test_update():
    mod_data = {'url': 'http://publisher.example.test/12346'}
    assetrequestlib.update(1, mod_data)
    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert asset_request['url'] == mod_data['url']
    assert asset_request['status'] == asset_request_statuses.pending.value


def test_reject():
    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert asset_request['status'] == asset_request_statuses.pending.value
    assetrequestlib.reject(1, approver=12)
    asset_request = assetrequestlib.get(1)
    assert asset_request['id'] == 1
    assert asset_request['status'] == asset_request_statuses.rejected.value
    asset = assetlib.get(1)
    assert asset['id'] == asset_request['id']
    assert asset['url'] != asset_request['url']


def test_cancel_pending():
    assetrequestlib.cancel(1, 123)
    asset_request = assetrequestlib.get(1)
    assert asset_request['status'] == asset_request_statuses.cancelled.value
