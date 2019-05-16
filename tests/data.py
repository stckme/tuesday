from hashlib import sha1


test_publication = dict(
    name='Test Publisher',
    domain='publisher.example.test'
)


test_commenter = dict(
    id=1,
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
    commenter_id=1,
    editors_pick=False,
    asset=test_asset_request_id,
    content="test comment",
    parent=1
)
