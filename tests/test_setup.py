import sys
sys.path.append('.')
import app.models


def suite_setup():
    app.models.destroy_db()
    app.models.setup_db()


def suite_teardown():
    app.models.destroy_db()
