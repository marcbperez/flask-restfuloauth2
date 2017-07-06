import pytest
import restfuloauth2
import urllib
import json
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
        client.post('/v1/dummy', follow_redirects=True, headers={
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
        client.post('/v1/dummy', follow_redirects=True, headers={
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
        client.post('/v1/dummy', follow_redirects=True, headers={
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
