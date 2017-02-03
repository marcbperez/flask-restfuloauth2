import pytest
import restfuloauth2
from restfuloauth2.database import db
from restfuloauth2.oauth.models import Client
import json
import urllib


@pytest.fixture
def client(request):
    """Configures the application and returns the test client."""
    restfuloauth2.app.config['TESTING'] = True
    restfuloauth2.app.config['SECRET_KEY'] = 'testing-key'

    db.drop_all(app=restfuloauth2.app)
    db.create_all(app=restfuloauth2.app)

    return restfuloauth2.app.test_client()


def create_user(client, username, password):
    """Creates a new user given a username and password."""
    rv = client.post('/v1/oauth/', follow_redirects=True, data={
        'submit': 'Add User',
        'username': username,
        'password': password,
    })


def create_client(client):
    """Creates a new client."""
    rv = client.post('/v1/oauth/', follow_redirects=True, data={
        'submit': 'Add Client',
    })

    db.app = restfuloauth2.app
    oauth_clients = Client.query.all()
    client_id = oauth_clients[0].client_id

    return client_id


def create_token(client, username, password, client_id):
    """Creates a new token given a username, password and client id."""
    rv = client.post('/v1/oauth/token', follow_redirects=True, data={
        'grant_type': 'password',
        'client_id': client_id,
        'username': username,
        'password': password
    })

    json_response = json.loads(rv.data)
    access_token = json_response['access_token']

    return access_token


def test_default_redirect(client):
    """Expects the default route to redirect to management."""
    rv = client.get('/', follow_redirects=True)
    assert 'Users' in rv.data
    assert 'Clients' in rv.data


def test_check(client):
    """Expects to obtain the authenticated user greeting."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    rv = client.get('/v1/oauth/check', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    })

    assert 'userA' in rv.data


def test_get_dummy_index(client):
    """Expects to get and empty index."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    rv = client.get('/v1/dummy', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    })

    assert '[]' in rv.data


def test_get_nonexistent_dummy(client):
    """Expects a not found error from a nonexistent item."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    rv = client.get('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    })

    assert rv.status_code == 404


def test_create_dummy(client):
    """Expects to create a new item."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    # Create the item.
    rv = client.post('/v1/dummy', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'public': 0,
    })

    assert rv.status_code == 201

    # Retrieve the new item.
    rv = client.get('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token})

    assert rv.status_code == 200


def test_update_dummy(client):
    """Expects to update an existing item."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    # Create the item.
    rv = client.post('/v1/dummy', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'public': 0,
    })

    # Get the item's etag.
    json_response = json.loads(rv.data)
    etag = json_response['etag']

    # Try a wrong etag and expect an error.
    rv = client.put('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'etag': etag + 'a',
        'public': 1,
    })

    assert rv.status_code != 201

    # Try with the right etag.
    rv = client.put('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'etag': etag,
        'public': 1,
    })

    assert rv.status_code == 201


def test_delete_dummy(client):
    """Expects to delete an existing item."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    # Create the item.
    rv = client.post('/v1/dummy', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'public': 0,
    })

    # Get the item's etag.
    json_response = json.loads(rv.data)
    etag = json_response['etag']

    # Try a wrong etag and expect an error.
    rv = client.delete('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'etag': etag + 'a',
    })

    assert rv.status_code != 204

    # Try with the right etag.
    rv = client.delete('/v1/dummy/1', follow_redirects=True, headers={
        'Authorization': 'Bearer ' + access_token
    }, data={
        'etag': etag,
    })

    assert rv.status_code == 204


def test_pagination(client):
    """Expects to get a paginated collection."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    # Create 20 new items.
    for i in range(20):
        rv = client.post('/v1/dummy', follow_redirects=True, headers={
            'Authorization': 'Bearer ' + access_token
        }, data={
            'public': 0,
        })

    # Get the paginated collection.
    rv = client.get(
        '/v1/dummy?page=2&max_results=5&sort=id-desc', follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    json_response = json.loads(rv.data)
    assert json_response[0]['id'] is 15
    assert len(json_response) is 5


def test_search(client):
    """Expects to search a collection."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    # Create 5 new items.
    for i in range(5):
        rv = client.post('/v1/dummy', follow_redirects=True, headers={
            'Authorization': 'Bearer ' + access_token
        }, data={
            'public': 0,
        })

    # Make a simple search by id.
    search = urllib.quote('{"column": "id","operator": "=","value": 3}')
    rv = client.get(
        '/v1/dummy?search=' + search, follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    json_response = json.loads(rv.data)
    assert json_response[0]['id'] is 3
    assert len(json_response) is 1

    # Try a wrong column operator and expect an error.
    wrong_column_operator = urllib.quote(
        '{"column": "id","operator": "x","value": 3}')
    rv = client.get(
        '/v1/dummy?search=' + wrong_column_operator, follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    assert rv.status_code == 401

    # Try a string value.
    search_text = urllib.quote(
        '{"column": "etag","operator": "!=","value": ""}')
    rv = client.get(
        '/v1/dummy?search=' + search_text, follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    json_response = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(json_response) is 5


def test_complex_search(client):
    """Expects to do a complex search on a collection."""
    create_user(client, 'userA', 'passA')
    client_id = create_client(client)
    access_token = create_token(client, 'userA', 'passA', client_id)

    search = urllib.quote('{\
      "operator": "and",\
      "conditions": [\
        {\
          "column": "id",\
          "operator": "=",\
          "value": 3\
        },\
        {\
          "operator": "or",\
          "conditions": [\
            {\
              "column": "public",\
              "operator": "=",\
              "value": 0\
            },\
            {\
              "column": "etag",\
              "operator": "!=",\
              "value": ""\
            }\
          ]\
        }\
      ]\
    }')

    wrong_condition_operator = urllib.quote('{\
      "operator": "x",\
      "conditions": [\
        {\
          "column": "id",\
          "operator": "=",\
          "value": 3\
        },\
        {\
          "column": "etag",\
          "operator": "!=",\
          "value": ""\
        }\
      ]\
    }')

    # Create 5 new items.
    for i in range(5):
        rv = client.post('/v1/dummy', follow_redirects=True, headers={
            'Authorization': 'Bearer ' + access_token
        }, data={
            'public': 0,
        })

    # Make a complex search configured with a JSON object.
    rv = client.get(
        '/v1/dummy?search=' + search, follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    json_response = json.loads(rv.data)
    assert json_response[0]['id'] is 3
    assert len(json_response) is 1

    # Try a wrong condition operator and expect an error.
    rv = client.get(
        '/v1/dummy?search=' + wrong_condition_operator, follow_redirects=True,
        headers={'Authorization': 'Bearer ' + access_token})

    assert rv.status_code == 401
