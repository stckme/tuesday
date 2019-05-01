from collections import namedtuple

import requests

from converge import settings
from apphelpers.errors import InvalidSessionError

import apphelpers.sessions as sessionslib


sessiondb_conn = dict(host=settings.SESSIONSDB_HOST,
                      port=settings.SESSIONSDB_PORT,
                      password=settings.SESSIONSDB_PASSWD,
                      db=settings.SESSIONSDB_NO)
sessionsdb = sessionslib.SessionDBHandler(sessiondb_conn)


class testdata:
    pass


class state:
    pass


Session = namedtuple('Session', ['uid', 'groups'])
testdata.session = Session(779988, ['editor', 'member'])
testdata.session_email = 'editor@example.com'
testdata.assetreqest_url = 'http://example.com/articles/7-places-to-visit'


def test_create_session():
    d = dict(uid=testdata.session.uid, groups=testdata.session.groups, \
             extras=dict(email=testdata.session_email))
    sid = sessionsdb.create(**d)
    assert len(sid) == 43
    sid_new = sessionsdb.create(testdata.session.uid, testdata.session.groups)
    assert sid == sid_new
    state.sid = sid


def test_whoami():
    headers = {'Authorization': state.sid}
    url = 'http://127.0.0.1:8000/whoami'
    user = requests.get(url, headers=headers).json()
    assert user['sid'] == state.sid
    assert user['id'] == testdata.session.uid
    assert user['groups'] == testdata.session.groups


def _test_create_asset_request(url, requester_id=None):
    headers = {'Authorization': state.sid}
    baseurl = 'http://127.0.0.1:8000/assetrequests/'
    data = {'url': url}
    if requester_id:
        data['requester'] = requester_id
    resp = requests.post(baseurl, json=data, headers=headers)
    asset_id = resp.json()
    assert isinstance(asset_id, str)

    url = baseurl + str(asset_id)
    resp = requests.get(url, headers=headers)
    asset_req = resp.json()
    assert asset_req['id'] == asset_id
    assert asset_req['url'] == data['url']
    assert asset_req['requester'] == testdata.session.uid

    return asset_id


def test_create_asset_request():
    state.assetreqest_id = _test_create_asset_request(testdata.assetreqest_url)


def test_create_asset_request_w_invalid_requster():
    invalid_requester_id = 99999
    assetreqest_id = _test_create_asset_request(url='http://example.com/article1', requester_id=invalid_requester_id)

    baseurl = 'http://127.0.0.1:8000/assetrequests/'
    url = baseurl + str(assetreqest_id)
    headers = {'Authorization': state.sid}
    resp = requests.get(url, headers=headers)
    asset_req = resp.json()
    assert asset_req['id'] == assetreqest_id
    assert asset_req['requester'] == testdata.session.uid
    assert asset_req['requester'] != invalid_requester_id


def test_approve_asset_request():
    baseurl = 'http://127.0.0.1:8000/assetrequests/'
    url = baseurl + str(state.assetreqest_id) + '/approve'
    headers = {'Authorization': state.sid}
    requests.post(url, headers=headers)

    baseurl = 'http://127.0.0.1:8000/assets/'
    url = baseurl + str(state.assetreqest_id)
    resp = requests.get(url, headers=headers).json()
    assert resp['url'] == testdata.assetreqest_url

    url = url + '/comments/count'
    resp = requests.get(url, headers=headers).json()
    assert resp == 0
