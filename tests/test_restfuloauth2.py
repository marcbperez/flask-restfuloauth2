import pytest
import restfuloauth2
from restfuloauth2.database import db
from common_methods import create_user, create_client, create_token


@pytest.fixture
def client():
    """Configures the application and returns the test client."""
    restfuloauth2.app.config['SECRET_KEY'] = 'testing-key'

    with restfuloauth2.app.app_context():
        db.drop_all()
        db.create_all()

    return restfuloauth2.app.test_client()


def test_check(client):
    """Expects to obtain the authenticated user greeting."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    rv = client.get('/v1/oauth/check', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    })

    assert 'userA' in rv.data


def test_default_oauth(client):
    """Expects the oauth route to redirect to management."""
    rv = client.get('/v1/oauth', follow_redirects=True)
    assert 'Users' in rv.data
    assert 'Clients' in rv.data


def test_default_redirect(client):
    """Expects the default route to show the service manifest."""
    rv = client.get('/', follow_redirects=True)
    assert 'swagger' in rv.data
