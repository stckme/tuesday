import requests
from requests import Session
from urllib.parse import urljoin
from apphelpers.errors import BaseError

from converge import settings


class SSOClientError(BaseError):
    pass


class PrefixedURLSession(Session):
    def __init__(self, baseurl, *args, **kw):
        super(PrefixedURLSession, self).__init__(*args, **kw)
        self.baseurl = baseurl

    def request(self, method, url, *args, **kw):
        url = urljoin(self.baseurl, url)
        return super(PrefixedURLSession, self).request(method, url, *args, **kw)


session = PrefixedURLSession(settings.SSO_API_URL)


def get_user_by_email(email):
    url = 'users/byemail/' + email
    resp = session.get(url)
    if resp.status_code == requests.codes.ok:
        return resp.json()
    raise SSOClientError(msg='Error while retriving user info', data={'email': email})


def update_user_groups(id, groups):
    resp = session.patch('users/{}/tuesday-groups'.format(id), json={'groups': groups})
    if resp.status_code == requests.codes.ok:
        return resp.json()
    raise SSOClientError(msg='Error while updating user groups', data={'id': id, 'groups': groups})
