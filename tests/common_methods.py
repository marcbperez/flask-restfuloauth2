import restfuloauth2
import json
from restfuloauth2.database import db
from restfuloauth2.oauth.models import Client


def create_user(client, username, password):
    """Creates a new user given a username and password."""
    client.post('/v1/oauth/', follow_redirects=True, data={
        'submit': 'Add User',
        'username': username,
        'password': password,
    })


def create_client(client):
    """Creates a new client."""
    client.post('/v1/oauth/', follow_redirects=True, data={
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
