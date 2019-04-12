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


test_approved_comments = [
    dict(commenter=1, editors_pick=False, asset=1, content="com 1", ip_address="127.0.0.1", parent=0),
    dict(commenter=2, editors_pick=False, asset=1, content="com 2", ip_address="127.0.0.1", parent=1),
    dict(commenter=1, editors_pick=False, asset=1, content="com 3", ip_address="127.0.0.1", parent=1),
    dict(commenter=2, editors_pick=False, asset=1, content="com 4", ip_address="127.0.0.1", parent=0),
    dict(commenter=1, editors_pick=False, asset=1, content="com 5", ip_address="127.0.0.1", parent=4),
    dict(commenter=2, editors_pick=False, asset=1, content="com 6", ip_address="127.0.0.1", parent=4),
    dict(commenter=3, editors_pick=False, asset=1, content="com 7", ip_address="127.0.0.1", parent=4),
    dict(commenter=3, editors_pick=False, asset=1, content="com 8", ip_address="127.0.0.1", parent=0),
    dict(commenter=2, editors_pick=False, asset=1, content="com 9", ip_address="127.0.0.1", parent=8),
    dict(commenter=1, editors_pick=False, asset=1, content="com 10", ip_address="127.0.0.1", parent=8),
    dict(commenter=1, editors_pick=False, asset=1, content="com 11", ip_address="127.0.0.1", parent=0)
]


test_pending_comments = [
    dict(commenter=1, editors_pick=False, asset=1, content="com 12", ip_address="127.0.0.1", parent=0),
    dict(commenter=2, editors_pick=False, asset=1, content="com 13", ip_address="127.0.0.1", parent=0),
    dict(commenter=3, editors_pick=False, asset=1, content="com 14", ip_address="127.0.0.1", parent=0),
    dict(commenter=2, editors_pick=False, asset=1, content="com 15", ip_address="127.0.0.1", parent=1),
    dict(commenter=3, editors_pick=False, asset=1, content="com 16", ip_address="127.0.0.1", parent=1),
    dict(commenter=1, editors_pick=False, asset=1, content="com 17", ip_address="127.0.0.1", parent=4),
    dict(commenter=2, editors_pick=False, asset=1, content="com 18", ip_address="127.0.0.1", parent=4),
    dict(commenter=2, editors_pick=False, asset=1, content="com 19", ip_address="127.0.0.1", parent=8),
    dict(commenter=3, editors_pick=False, asset=1, content="com 20", ip_address="127.0.0.1", parent=8)
]