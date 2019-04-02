from app.models import setup_db, destroy_db


def suite_setup():
    destroy_db()
    setup_db()


def suite_teardown():
    destroy_db()
    setup_db()
