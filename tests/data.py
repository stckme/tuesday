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


test_asset_request = dict(
    url='http://publisher.example.test/1234',
    requester=123
)


test_new_publication_asset_request = dict(
    url='http://publication.example.com/234',
    requester=123
)


test_comment = dict(
    commenter=1,
    editors_pick=False,
    asset=1,
    content="test comment",
    ip_address="127.0.0.1",
    parent=1
)
