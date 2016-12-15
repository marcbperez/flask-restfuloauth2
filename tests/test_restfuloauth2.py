import pytest
import restfuloauth2


@pytest.fixture
def client(request):
    restfuloauth2.app.config['TESTING'] = True
    client = restfuloauth2.app.test_client()

    return client


def test_default_redirect(client):
    rv = client.get('/', follow_redirects=True)
    assert 'Users' in rv.data
    assert 'Clients' in rv.data
