from app.libs import asset as assetlib
from app.libs import comment as commentlib
from app.libs import commenter as commenterlib
from app.libs import publication as publicationlib
from app.libs import asset_request as assetrequestlib
from app.libs import pending_comment as pendingcommentlib
from app.libs import comment_action_log as commentactionloglib
from app.models import setup_db, destroy_db, asset_request_statuses, comment_actions

from tests.data import test_commenter, test_publication, test_comment
from tests.data import test_new_publication_asset_request, test_asset_request
from tests.data import test_approved_comments, test_pending_comments


def test_suite_setup():
    destroy_db()
    setup_db()

    commenterlib.create(**test_commenter)
    test_commenter['uid'] = 2
    test_commenter['username'] = 'tester2'
    commenterlib.create(**test_commenter)
    test_commenter['uid'] = 3
    test_commenter['username'] = 'tester3'
    commenterlib.create(**test_commenter)

    publicationlib.create(**test_publication)
    asset_req_id = assetrequestlib.create(**test_asset_request)
    assetrequestlib.approve(asset_req_id, approver=12)

    for comment in test_approved_comments:
        comment_id = pendingcommentlib.create(**comment)
        pendingcommentlib.approve(comment_id)

    for comment in test_pending_comments:
        comment_id = pendingcommentlib.create(**comment)


def test_count():
    assert len(pendingcommentlib.list_()) == 9
    assert len(commentlib.list_()) == 11


def test_fetch_comments_for_anonymous_user():
    comments = assetlib.get_user_accesible_comments(
        1, user=None, parent=0, last_comment=None, limit=10, children_limit=None
    )
    assert len(comments) == 4
    assert sum([len(c.get('replies', [])) for c in comments]) == 7

    comments = assetlib.get_user_accesible_comments(
        1, user=None, parent=0, last_comment=8, limit=10, children_limit=None
    )
    assert len(comments) == 2
    assert sum([len(c.get('replies', [])) for c in comments]) == 5

    comments = assetlib.get_user_accesible_comments(
        1, user=None, parent=0, last_comment=1, limit=10, children_limit=None
    )
    assert len(comments) == 0
    assert sum([len(c.get('replies', [])) for c in comments]) == 0



def test_fetch_comments_for_commenter():
    comments = assetlib.get_user_accesible_comments(
        1, user=1, parent=0, last_comment=None, limit=10, children_limit=None
    )
    assert len(comments) == 5
    assert sum([len(c.get('replies', [])) for c in comments]) == 8

    comments = assetlib.get_user_accesible_comments(
        1, user=2, parent=0, last_comment=None, limit=10, children_limit=None
    )
    assert len(comments) == 5
    assert sum([len(c.get('replies', [])) for c in comments]) == 10

    comments = assetlib.get_user_accesible_comments(
        1, user=3, parent=0, last_comment=None, limit=10, children_limit=None
    )
    assert len(comments) == 5
    assert sum([len(c.get('replies', [])) for c in comments]) == 9
