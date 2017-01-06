import pytest
import restfuloauth2
from restfuloauth2.database import db
from restfuloauth2.oauth.models import Client


@pytest.fixture
def client(request):
    restfuloauth2.app.config['TESTING'] = True
    restfuloauth2.app.config['SECRET_KEY'] = 'testing-key'

    db.drop_all(app=restfuloauth2.app)
    db.create_all(app=restfuloauth2.app)

    return restfuloauth2.app.test_client()


def test_default_redirect(client):
    rv = client.get('/', follow_redirects=True)
    assert 'Users' in rv.data
    assert 'Clients' in rv.data


def test_create_token(client):
    rv = client.post('/v1/oauth/', follow_redirects=True, data={
        'submit': 'Add User',
        'username': 'userA',
        'password': 'passA',
    })

    rv = client.post('/v1/oauth/', follow_redirects=True, data={
        'submit': 'Add Client',
    })

    db.app = restfuloauth2.app
    oauth_client = Client.query.all()

    rv = client.post('/v1/oauth/token', follow_redirects=True, data={
        'grant_type': 'password',
        'client_id': oauth_client[0].client_id,
        'username': 'userA',
        'password': 'passA'
    })

    assert 'access_token' in rv.data
