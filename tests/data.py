from hashlib import sha1


test_publication = dict(
    name='Test Publisher',
    domain='publisher.example.test'
)


test_commenter = dict(
    uid=1,
    username='tester',
    name='test user',
    bio='I am a tester',
    web='publisher.test.in'
)


url = 'http://publisher.example.test/1234'
test_asset_request = dict(
    url=url,
    requester=123
)
test_asset_request_id = sha1(bytes(url, 'utf8')).hexdigest()


url = 'http://publication.example.com/234'
test_new_publication_asset_request = dict(
    url=url,
    requester=123
)
test_new_publication_asset_request_id = sha1(bytes(url, 'utf8')).hexdigest()


test_comment = dict(
    commenter=1,
    editors_pick=False,
    asset=test_asset_request_id,
    content="test comment",
    ip_address="127.0.0.1",
    parent=1
)
