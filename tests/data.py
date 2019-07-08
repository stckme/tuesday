from hashlib import sha1


test_publication = dict(
    name='Test Publisher',
    domain='publisher.example.test'
)


test_commenter = dict(
    id=1,
    name='test user',
    email='dev@test.com',
    bio='I am a tester'
)


url = 'http://publisher.example.test/1234'
test_asset_request = dict(
    url=url,
    requester=123,
    title="Test Asset Request"
)
test_asset_request_id = sha1(bytes(url, 'utf8')).hexdigest()


url = 'http://publication.example.com/234'
test_new_publication_asset_request = dict(
    url=url,
    requester=123,
    title="Test Asset"
)
test_new_publication_asset_request_id = sha1(bytes(url, 'utf8')).hexdigest()


test_comment = dict(
    commenter_id=1,
    editors_pick=False,
    asset=test_asset_request_id,
    content="test comment",
    parent=0
)
