from app.libs import asset as assetlib
from app.libs import comment as commentlib
from app.libs import commenter as commenterlib
from app.libs import publication as publicationlib
from app.libs import asset_request as assetrequestlib
from app.libs import pending_comment as pendingcommentlib
from app.libs import archived_comment as archivedcommentlib
from app.libs import rejected_comment as rejectedcommentlib
from app.libs import comment_action_log as commentactionloglib
from app.models import setup_db, destroy_db, asset_request_statuses, comment_actions

from tests.data import test_commenter, test_publication, test_comment
from tests.data import test_new_publication_asset_request, test_asset_request


def test_suite_setup():
    destroy_db()
    setup_db()
    commenterlib.create(**test_commenter)
    publicationlib.create(**test_publication)
    asset_req_id = assetrequestlib.create(**test_asset_request)
    assetrequestlib.approve(asset_req_id, approver=12)


def test_create():
    pending_comment_id = pendingcommentlib.create(**test_comment)
    assert pending_comment_id == 1
    pending_comment = pendingcommentlib.get(pending_comment_id)
    assert pending_comment != None


def test_get():
    comment = pendingcommentlib.get(1)
    assert comment['id'] == 1
    assert test_comment.items() < comment.items()


def test_accept():
    assert not commentlib.exists(1)
    assert pendingcommentlib.exists(1)

    pending_comment = pendingcommentlib.get(1)
    pendingcommentlib.approve(1)

    assert not pendingcommentlib.exists(1)
    assert commentlib.exists(1)
    comment = commentlib.get(1)
    assert pending_comment['id'] == comment['id']

    logs = commentactionloglib.list_by_comment(1, 1, 10)
    assert len(logs) == 1
    assert logs[0]["action"] == comment_actions.approved.value


def test_list_accepted():
    assert len(commentlib.list_()) == 1
    assert len(commentlib.list_(page=2, size=50)) == 0


def test_update_accepted():
    comment = commentlib.get(1)
    commentlib.update(1, {'editors_pick': True})
    updated_comment = commentlib.get(1)
    assert comment['editors_pick'] != updated_comment['editors_pick']

    logs = commentactionloglib.list_()
    assert len(logs) == 2
    assert logs[0]["action"] == comment_actions.picked.value


def test_archive():
    assert commentlib.exists(1)
    assert not archivedcommentlib.exists(1)

    comment = commentlib.get(1)
    archived_id = commentlib.archive(1)

    assert not commentlib.exists(archived_id)
    assert archivedcommentlib.exists(archived_id)
    archived_comment = archivedcommentlib.get(archived_id)
    assert archived_comment['id'] == comment['id']


def test_list_archived():
    assert len(archivedcommentlib.list_()) == 1
    assert len(archivedcommentlib.list_(page=2, size=50)) == 0


def test_update_pending():
    pending_comment_id = pendingcommentlib.create(**test_comment)
    comment = pendingcommentlib.get(pending_comment_id)
    pendingcommentlib.update(
        pending_comment_id,
        {'content': 'updated content', 'editors_pick': True}
    )
    updated_comment = pendingcommentlib.get(pending_comment_id)
    assert comment['content'] != updated_comment['content']

    logs = commentactionloglib.list_()
    assert len(logs) == 3
    assert logs[0]["action"] == comment_actions.picked.value


def test_list_pending():
    assert len(pendingcommentlib.list_()) == 1
    assert len(pendingcommentlib.list_(page=2, size=50)) == 0


def test_reject():
    pending_comment_id = 2
    assert pendingcommentlib.exists(pending_comment_id)
    assert not rejectedcommentlib.exists(pending_comment_id)

    pending_comment = pendingcommentlib.get(pending_comment_id)
    note = 'invalid comment'
    rejected_id = pendingcommentlib.reject(pending_comment_id, note)

    assert not pendingcommentlib.exists(pending_comment_id)
    assert rejectedcommentlib.exists(rejected_id)
    rejected_comment = rejectedcommentlib.get(rejected_id)
    assert rejected_comment['note'] == note
    assert pending_comment.items() < rejected_comment.items()

    logs = commentactionloglib.list_(page=1, size=10)
    assert len(logs) == 4
    assert logs[0]["action"] == comment_actions.rejected.value


def test_list_rejected():
    assert len(rejectedcommentlib.list_()) == 1
    assert len(rejectedcommentlib.list_(page=2, size=50)) == 0
